
from typing import Any, Dict, Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from maintenance_report_generator import build_maintenance_report



# Accept only machine_data as input for compatibility with the frontend
class MaintenanceRequest(BaseModel):
    machine_data: Dict[str, Any]


class MaintenanceResponse(BaseModel):
    machine_status: str
    severity: str
    urgency: str
    failure_probability: str
    summary: str
    top_risk_factors: list[str]
    possible_causes: list[str]
    recommended_actions: list[str]
    downtime_risk: str
    performance_impact: str
    confidence_note: str


app = FastAPI(
    title="Predictive Maintenance API",
    version="1.0.0",
    description="Structured maintenance report generator powered by Gemini and ML predictions.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "service": "Predictive Maintenance API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate-report", response_model=MaintenanceResponse)
def generate_report(payload: MaintenanceRequest):
    try:
        # Use default values for prediction_class and failure_probability
        report = build_maintenance_report(
            prediction_class=0,  # or use your model logic here
            failure_probability=0.0,  # or use your model logic here
            machine_data=payload.machine_data,
        )
        return report
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate maintenance report: {exc}") from exc
