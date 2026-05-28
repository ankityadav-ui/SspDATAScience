import argparse
import json
import os
import sys
import time
from pathlib import Path

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field


class MaintenanceAssessment(BaseModel):
    machine_status: str = Field(..., description="Overall machine status")
    severity: str = Field(..., description="Severity level")
    urgency: str = Field(..., description="Urgency level")
    failure_probability: str = Field(..., description="Failure probability as percentage string")
    summary: str = Field(..., description="Concise maintenance summary")
    top_risk_factors: list[str] = Field(..., description="Primary risk factors")
    possible_causes: list[str] = Field(..., description="Likely causes")
    recommended_actions: list[str] = Field(..., description="Recommended actions")
    downtime_risk: str = Field(..., description="Downtime risk statement")
    performance_impact: str = Field(..., description="Performance impact statement")
    confidence_note: str = Field(..., description="Confidence explanation")


def _load_env_file():
    env_path = Path(__file__).with_name('.env')
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or '=' not in stripped:
            continue

        key, value = stripped.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file()


def _build_fallback_report(prediction_class, failure_probability, machine_data):
    try:
        probability_value = float(failure_probability)
    except (TypeError, ValueError):
        probability_value = 0.0

    machine_snapshot = machine_data if isinstance(machine_data, dict) else {}
    temperature_difference = float(machine_snapshot.get("temperature_difference", 0) or 0)
    vibration_level = float(machine_snapshot.get("vibration_level", 0) or 0)
    tool_wear = machine_snapshot.get("tool_wear_min")
    operational_hours = float(machine_snapshot.get("operational_hours", 0) or 0)

    if str(prediction_class).strip() in {"1", "True", "true", "failure", "high"} or probability_value >= 0.75:
        severity = "Critical"
        urgency = "Immediate"
        machine_status = "At Risk"
    elif probability_value >= 0.45 or temperature_difference >= 10 or vibration_level >= 40:
        severity = "Moderate"
        urgency = "High"
        machine_status = "Monitor Closely"
    else:
        severity = "Low"
        urgency = "Monitor"
        machine_status = "Operational"

    top_risk_factors = []
    if tool_wear in (None, "", "nan"):
        top_risk_factors.append("Missing tool wear data limits wear assessment.")
    if temperature_difference >= 10:
        top_risk_factors.append("Elevated thermal stress detected.")
    if vibration_level >= 40:
        top_risk_factors.append("High vibration may indicate mechanical imbalance.")
    if operational_hours >= 1000 and probability_value >= 0.4:
        top_risk_factors.append("Long service hours increase wear-related risk.")
    if not top_risk_factors:
        top_risk_factors.append("Sensor readings are within normal working range.")

    possible_causes = []
    if temperature_difference >= 10:
        possible_causes.append("Thermal stress or cooling inefficiency.")
    if vibration_level >= 40:
        possible_causes.append("Mechanical imbalance, bearing wear, or alignment drift.")
    if tool_wear in (None, "", "nan"):
        possible_causes.append("Missing wear measurement leaves the component condition uncertain.")
    if not possible_causes:
        possible_causes.append("No immediate abnormality detected from the provided snapshot.")

    recommended_actions = [
        "Continue monitoring the machine and compare against baseline sensor trends.",
        "Inspect temperature, vibration, and wear measurements if conditions worsen.",
    ]
    if severity == "Critical":
        recommended_actions.insert(0, "Escalate maintenance inspection immediately.")
    elif severity == "Moderate":
        recommended_actions.insert(0, "Schedule a maintenance review within the next shift.")

    return {
        "machine_status": machine_status,
        "severity": severity,
        "urgency": urgency,
        "failure_probability": f"{probability_value * 100:.2f}%",
        "summary": (
            f"ML prediction {prediction_class} with estimated failure probability {probability_value * 100:.2f}% indicates {machine_status.lower()}. "
            "Local fallback assessment was used because external structured generation was unavailable."
        ),
        "top_risk_factors": top_risk_factors,
        "possible_causes": possible_causes,
        "recommended_actions": recommended_actions,
        "downtime_risk": (
            "High" if severity == "Critical" else "Moderate" if severity == "Moderate" else "Low"
        ),
        "performance_impact": (
            "Significant" if severity == "Critical" else "Potential" if severity == "Moderate" else "Minimal"
        ),
        "confidence_note": (
            "Fallback local assessment generated because Gemini structured generation was unavailable; rerun when the external API is reachable."
        ),
    }


def build_maintenance_report(prediction_class, failure_probability, machine_data):
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set")

    parser = PydanticOutputParser(pydantic_object=MaintenanceAssessment)

    prompt = PromptTemplate(
        template=(
            "You are an industrial AI maintenance assistant. Use the ML prediction and machine sensor snapshot to generate a concise professional maintenance assessment. "
            "Do not override the prediction result. Base reasoning only on the given data. Focus on thermal stress, torque, wear, RPM, vibration, and maintenance history where relevant.\n\n"
            "Prediction Class: {prediction_class}\n"
            "Failure Probability: {failure_probability}\n"
            "Machine Data: {machine_data}\n\n"
            "Return structured output only in the requested schema.\n"
            "{format_instructions}"
        ),
        input_variables=["prediction_class", "failure_probability", "machine_data"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=google_api_key,
        temperature=0.2,
    )

    chain = prompt | llm | parser

    last_error = None
    for attempt in range(3):
        try:
            report = chain.invoke({
                "prediction_class": str(prediction_class),
                "failure_probability": str(failure_probability),
                "machine_data": json.dumps(machine_data, ensure_ascii=True),
            })
            break
        except Exception as exc:
            last_error = exc
            wait_time = 2 ** attempt
            print(
                f"Gemini report generation attempt {attempt + 1} failed: {exc}. Retrying in {wait_time}s.",
                file=sys.stderr,
            )
            if attempt == 2:
                report = _build_fallback_report(prediction_class, failure_probability, machine_data)
                print(
                    f"Falling back to local maintenance assessment after Gemini failures: {last_error}",
                    file=sys.stderr,
                )
                return report
            time.sleep(wait_time)

    if isinstance(report, MaintenanceAssessment):
        return report.model_dump()
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Generate a structured maintenance assessment report using LangChain and Gemini."
    )
    parser.add_argument(
        "--prediction-class",
        required=True,
        help="Prediction label, such as 1 for failure risk or 0 for healthy",
    )
    parser.add_argument(
        "--failure-probability",
        required=True,
        type=float,
        help="Failure probability as a decimal between 0 and 1",
    )
    parser.add_argument(
        "--machine-data",
        required=True,
        help="Machine sensor data as JSON string",
    )

    args = parser.parse_args()

    try:
        machine_data = json.loads(args.machine_data)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid machine-data JSON: {exc}") from exc

    report = build_maintenance_report(args.prediction_class, args.failure_probability, machine_data)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
