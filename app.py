import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime

# =========================================================
# PredictX - Predictive Maintenance Dashboard
# =========================================================

st.set_page_config(
    page_title="PredictX Dashboard",
    page_icon="⚙️",
    layout="wide"
)

# ---------------------------------------------------------
# ThingSpeak configuration
# ---------------------------------------------------------

CHANNEL_ID = "3510240"

try:
    READ_API_KEY = st.secrets["THINGSPEAK_READ_API_KEY"]
except Exception:
    st.error("❌ ThingSpeak Read API Key is not configured.")
    st.info(
        "Add THINGSPEAK_READ_API_KEY to Streamlit Cloud → "
        "Settings → Secrets."
    )
    st.stop()


# ---------------------------------------------------------
# Get data from ThingSpeak
# ---------------------------------------------------------

@st.cache_data(ttl=15)
def get_thingspeak_data():

    url = (
        f"https://api.thingspeak.com/channels/"
        f"{CHANNEL_ID}/feeds.json"
    )

    params = {
        "api_key": READ_API_KEY,
        "results": 100
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    feeds = data.get("feeds", [])

    if not feeds:
        return pd.DataFrame()

    rows = []

    for feed in feeds:

        rows.append({
            "Time": feed.get("created_at"),

            "Temperature": pd.to_numeric(
                feed.get("field1"),
                errors="coerce"
            ),

            "Current": pd.to_numeric(
                feed.get("field2"),
                errors="coerce"
            ),

            "Voltage": pd.to_numeric(
                feed.get("field3"),
                errors="coerce"
            ),

            "Vibration": pd.to_numeric(
                feed.get("field4"),
                errors="coerce"
            )
        })

    df = pd.DataFrame(rows)

    df["Time"] = pd.to_datetime(
        df["Time"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "Temperature",
            "Current",
            "Voltage",
            "Vibration"
        ]
    )

    return df


# ---------------------------------------------------------
# Diagnosis
# ---------------------------------------------------------

def diagnose(row):

    temperature = row["Temperature"]
    current = row["Current"]
    voltage = row["Voltage"]
    vibration = row["Vibration"]

    problems = []

    if temperature > 60:
        problems.append("High temperature detected")

    if current > 4:
        problems.append("High current detected")

    if voltage > 22:
        problems.append("High voltage detected")

    if vibration > 8:
        problems.append("High vibration detected")

    # No abnormal condition
    if not problems:

        return (
            "NORMAL",
            "System operating normally.",
            "No immediate action required.",
            5
        )

    # Multiple abnormal conditions
    if len(problems) >= 2:

        return (
            "CRITICAL",
            "Multiple abnormal sensor conditions detected.",
            "Inspect the system immediately and check for electrical or mechanical faults.",
            90
        )

    # Single abnormal condition
    problem = problems[0]

    if "current" in problem.lower():

        return (
            "FAILURE RISK",
            "High current detected — possible electrical overload or fault.",
            "Check for electrical overload or electrical fault.",
            75
        )

    if "voltage" in problem.lower():

        return (
            "FAILURE RISK",
            "Abnormal voltage detected.",
            "Inspect the power supply and electrical connections.",
            75
        )

    if "temperature" in problem.lower():

        return (
            "FAILURE RISK",
            "High temperature detected.",
            "Check cooling, ventilation and possible overheating.",
            75
        )

    if "vibration" in problem.lower():

        return (
            "FAILURE RISK",
            "High vibration detected.",
            "Inspect mechanical alignment, bearings and mounting.",
            75
        )

    return (
        "WARNING",
        "Abnormal sensor reading detected.",
        "Inspect the system.",
        60
    )


# ---------------------------------------------------------
# Dashboard title
# ---------------------------------------------------------

st.title("⚙️ PredictX")
st.subheader("AI-Powered Predictive Maintenance Dashboard")

st.write(
    "Monitor → Predict → Diagnose → Prevent"
)

st.divider()


# ---------------------------------------------------------
# Load ThingSpeak data
# ---------------------------------------------------------

try:

    df = get_thingspeak_data()

except Exception as e:

    st.error("❌ Could not connect to ThingSpeak.")

    st.code(str(e))

    st.info(
        "Check your ThingSpeak Read API Key, Channel ID "
        "and internet connection."
    )

    st.stop()


if df.empty:

    st.warning("⚠️ No sensor data available yet.")

    st.stop()


# ---------------------------------------------------------
# Latest reading
# ---------------------------------------------------------

latest = df.iloc[-1]

temperature = latest["Temperature"]
current = latest["Current"]
voltage = latest["Voltage"]
vibration = latest["Vibration"]


# ---------------------------------------------------------
# Diagnosis
# ---------------------------------------------------------

status, diagnosis, action, risk = diagnose(latest)


# ---------------------------------------------------------
# Latest readings
# ---------------------------------------------------------

st.header("📊 Latest Sensor Readings")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🌡️ Temperature",
        f"{temperature:.2f} °C"
    )

with col2:
    st.metric(
        "⚡ Current",
        f"{current:.2f} A"
    )

with col3:
    st.metric(
        "🔌 Voltage",
        f"{voltage:.2f} V"
    )

with col4:
    st.metric(
        "〰️ Vibration",
        f"{vibration:.2f}"
    )


st.divider()


# ---------------------------------------------------------
# System status
# ---------------------------------------------------------

st.header("🚦 System Status")

if status == "NORMAL":

    st.success("✅ SYSTEM STATUS: NORMAL")

elif status == "WARNING":

    st.warning("⚠️ SYSTEM STATUS: WARNING")

else:

    st.error("🚨 SYSTEM STATUS: FAILURE RISK")


col1, col2 = st.columns(2)

with col1:

    st.subheader("🔍 Diagnosis")

    st.write(diagnosis)

with col2:

    st.subheader("🛠️ Recommended Action")

    st.write(action)


# ---------------------------------------------------------
# Failure risk
# ---------------------------------------------------------

st.subheader("📈 Failure Risk")

st.progress(
    min(risk, 100) / 100
)

st.write(
    f"Estimated failure risk: **{risk}%**"
)


st.divider()


# ---------------------------------------------------------
# Sensor trend charts
# ---------------------------------------------------------

st.header("📈 Sensor Trend Analysis")

# Temperature
fig_temp = go.Figure()

fig_temp.add_trace(
    go.Scatter(
        x=df["Time"],
        y=df["Temperature"],
        mode="lines+markers",
        name="Temperature"
    )
)

fig_temp.update_layout(
    title="Temperature Trend",
    xaxis_title="Time",
    yaxis_title="Temperature (°C)",
    height=400
)

st.plotly_chart(
    fig_temp,
    use_container_width=True
)


# Current
fig_current = go.Figure()

fig_current.add_trace(
    go.Scatter(
        x=df["Time"],
        y=df["Current"],
        mode="lines+markers",
        name="Current"
    )
)

fig_current.update_layout(
    title="Current Trend",
    xaxis_title="Time",
    yaxis_title="Current (A)",
    height=400
)

st.plotly_chart(
    fig_current,
    use_container_width=True
)


# Voltage
fig_voltage = go.Figure()

fig_voltage.add_trace(
    go.Scatter(
        x=df["Time"],
        y=df["Voltage"],
        mode="lines+markers",
        name="Voltage"
    )
)

fig_voltage.update_layout(
    title="Voltage Trend",
    xaxis_title="Time",
    yaxis_title="Voltage (V)",
    height=400
)

st.plotly_chart(
    fig_voltage,
    use_container_width=True
)


# Vibration
fig_vibration = go.Figure()

fig_vibration.add_trace(
    go.Scatter(
        x=df["Time"],
        y=df["Vibration"],
        mode="lines+markers",
        name="Vibration"
    )
)

fig_vibration.update_layout(
    title="Vibration Trend",
    xaxis_title="Time",
    yaxis_title="Vibration",
    height=400
)

st.plotly_chart(
    fig_vibration,
    use_container_width=True
)


# ---------------------------------------------------------
# Recent readings
# ---------------------------------------------------------

st.divider()

st.header("🧾 Recent Sensor Readings")

display_df = df.copy()

display_df["Time"] = display_df["Time"].dt.strftime(
    "%Y-%m-%d %H:%M:%S"
)

st.dataframe(
    display_df.tail(10).iloc[::-1],
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# System information
# ---------------------------------------------------------

st.divider()

st.caption(
    f"ThingSpeak Channel: {CHANNEL_ID} | "
    f"Total readings loaded: {len(df)}"
)

st.caption(
    "PredictX prototype — sensor data from ESP32/Wokwi "
    "via ThingSpeak."
)
