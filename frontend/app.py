import requests
import streamlit as st


st.set_page_config(
    page_title="Predictive Maintenance Studio",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="auto",
)

# Light theme custom CSS
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(120deg, #f8fafc 0%, #e0e7ef 100%) !important;
    }
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 2.5rem;
    }
    .glass-panel {
        background: rgba(255,255,255,0.92);
        border: 1px solid #e0e7ef;
        box-shadow: 0 8px 32px rgba(0,0,0,0.07);
        border-radius: 18px;
        padding: 1.2rem 1.2rem 1.1rem 1.2rem;
        margin-bottom: 1.2rem;
    }
    .section-title {
        font-size: 1.18rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.4rem;
    }
    .subtle-text {
        color: #64748b;
        font-size: 0.97rem;
    }
    .metric-card {
        background: #f1f5f9;
        border: 1px solid #e0e7ef;
        border-radius: 14px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.7rem;
    }
    .metric-label {
        color: #64748b;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
    }
    .metric-value {
        color: #1e293b;
        font-size: 1.5rem;
        font-weight: 800;
        margin-top: 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

API_URL = "https://sspdatascience.onrender.com/generate-report"

# Header
st.markdown(
    """
    <div class="glass-panel" style="margin-bottom:2.2rem;">
        <div style="display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap;">
            <div>
                <div style="font-size: 2.1rem; font-weight: 800; color:#1e293b;">Predictive Maintenance Studio</div>
                <div class="subtle-text" style="margin-top:0.35rem;">
                    Generate structured maintenance assessments with a clean operational dashboard and a FastAPI backend.
                </div>
            </div>
            <div style="display:flex; align-items:center; gap:0.5rem; background:#e0fce7; border:1px solid #22c55e; border-radius:999px; padding:0.45rem 0.8rem; color:#15803d; font-size:0.78rem; font-weight:700;">
                <span style="display:inline-block; width:0.55rem; height:0.55rem; border-radius:999px; background:#22c55e;"></span>
                Live AI report workflow
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

sample_machine_data = {
    "machine_type": "M",
    "factory_section": "Production",
    "shift": "Night",
    "air_temperature_K": 302.5,
    "process_temperature_K": 312.0,
    "temperature_difference": 9.5,
    "humidity_percent": 78,
    "rotational_speed_rpm": 1500,
    "torque_Nm": 50,
    "pressure_bar": 4.2,
    "tool_wear_min": 180,
    "vibration_level": "High",
    "operational_hours": 120,
    "energy_consumption_kwh": 130.5,
    "maintenance_history": "Average",
    "stress_score": 75.0,
}


# --- UI Layout: Full-width, centered form, modern grid ---
st.markdown('<div class="glass-panel" style="max-width:1200px;margin:0 auto 2.2rem auto;">'
            '<div class="section-title">Input Controls</div>'
            '<div class="subtle-text">Tune the machine state and trigger the structured maintenance assessment.</div>'
            '</div>', unsafe_allow_html=True)

with st.form("maintenance_form"):
    grid = st.columns([1, 1, 1, 1], gap="large")
    with grid[0]:
        machine_type = st.selectbox("Machine type", ["M", "L", "H"], index=0)
        factory_section = st.selectbox("Factory section", ["Production", "Assembly", "Quality"], index=0)
        shift = st.selectbox("Shift", ["Night", "Day", "Evening"], index=0)
        vibration_level = st.selectbox("Vibration level", ["Low", "Medium", "High"], index=2)
    with grid[1]:
        air_temperature_K = st.number_input("Air temperature (K)", value=sample_machine_data["air_temperature_K"], step=0.1)
        process_temperature_K = st.number_input("Process temperature (K)", value=sample_machine_data["process_temperature_K"], step=0.1)
        temperature_difference = st.number_input("Temperature difference", value=sample_machine_data["temperature_difference"], step=0.1)
        humidity_percent = st.number_input("Humidity (%)", value=sample_machine_data["humidity_percent"], step=1)
    with grid[2]:
        rotational_speed_rpm = st.number_input("Rotational speed (RPM)", value=sample_machine_data["rotational_speed_rpm"], step=10)
        torque_Nm = st.number_input("Torque (Nm)", value=sample_machine_data["torque_Nm"], step=1)
        pressure_bar = st.number_input("Pressure (bar)", value=sample_machine_data["pressure_bar"], step=0.1)
        tool_wear_min = st.number_input("Tool wear (min)", value=sample_machine_data["tool_wear_min"], step=5)
    with grid[3]:
        operational_hours = st.number_input("Operational hours", value=sample_machine_data["operational_hours"], step=1)
        energy_consumption_kwh = st.number_input("Energy consumption (kWh)", value=sample_machine_data["energy_consumption_kwh"], step=0.5)
        maintenance_history = st.selectbox("Maintenance history", ["Good", "Average", "Poor"], index=1)
        stress_score = st.number_input("Stress score", value=sample_machine_data["stress_score"], step=1.0)

    submitted = st.form_submit_button("Generate maintenance report", use_container_width=True)

machine_data = {
    "machine_type": machine_type,
    "factory_section": factory_section,
    "shift": shift,
    "air_temperature_K": air_temperature_K,
    "process_temperature_K": process_temperature_K,
    "temperature_difference": temperature_difference,
    "humidity_percent": humidity_percent,
    "rotational_speed_rpm": rotational_speed_rpm,
    "torque_Nm": torque_Nm,
    "pressure_bar": pressure_bar,
    "tool_wear_min": tool_wear_min,
    "vibration_level": vibration_level,
    "operational_hours": operational_hours,
    "energy_consumption_kwh": energy_consumption_kwh,
    "maintenance_history": maintenance_history,
    "stress_score": stress_score,
}

if submitted:
    payload = {
        "machine_data": machine_data,
    }
    with st.spinner("Calling FastAPI backend..."):
        try:
            response = requests.post(API_URL, json=payload, timeout=120)
            response.raise_for_status()
            report = response.json()
            st.session_state["report"] = report
        except requests.exceptions.RequestException as exc:
            st.error(f"Backend request failed: {exc}")

# --- Output section always below input ---
st.markdown('<div class="glass-panel"><div class="section-title">Operational snapshot</div><div class="subtle-text">Live assessment summary and key risk indicators.</div></div>', unsafe_allow_html=True)

if "report" in st.session_state:
    report = st.session_state["report"]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Machine Status</div><div class="metric-value">{report["machine_status"]}</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Severity</div><div class="metric-value">{report["severity"]}</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Urgency</div><div class="metric-value">{report["urgency"]}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<div class="glass-panel"><div class="section-title">Summary</div><div class="subtle-text" style="font-size: 1.02rem; line-height:1.5;">{report["summary"]}</div></div>',
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown('<div class="glass-panel"><div class="section-title">Risk factors</div></div>', unsafe_allow_html=True)
        for factor in report["top_risk_factors"]:
            st.markdown(f"- {factor}", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="glass-panel"><div class="section-title">Recommended actions</div></div>', unsafe_allow_html=True)
        for action in report["recommended_actions"]:
            st.markdown(f"- {action}", unsafe_allow_html=True)

    st.markdown(
        f'<div class="glass-panel"><div class="section-title">Confidence note</div><div class="subtle-text">{report["confidence_note"]}</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="glass-panel"><div class="section-title">Failure probability</div><div class="subtle-text">{report["failure_probability"]}</div></div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="glass-panel"><div class="section-title">Waiting for report</div><div class="subtle-text">Submit the input form to generate a structured maintenance assessment.</div></div>',
        unsafe_allow_html=True,
    )
