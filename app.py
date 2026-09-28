import streamlit as st
import requests
import pandas as pd
import time

# -----------------------------
# PredictX Dashboard
# -----------------------------

st.set_page_config(
    page_title="PredictX Dashboard",
    page_icon="⚙️",
    layout="wide"
)

# -----------------------------
# Title
# -----------------------------

st.title("⚙️ PredictX")
st.subheader("AI-Powered Predictive Maintenance Dashboard")

st.write(
    "Monitor temperature, current, voltage and vibration "
    "data from the PredictX sensor system."
)

# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.header("ThingSpeak Settings")

channel_id = st.sidebar.text_input(
    "ThingSpeak Channel ID",
    value="3510240"
)

read_api_key = st.sidebar.text_input(
    "ThingSpeak Read API Key",
    type="password"
)

number_of_readings = st.sidebar.slider(
    "Number of readings",
    min_value=10,
    max_value=100,
    value=30
)

refresh = st.sidebar.button("🔄 Refresh Data")

# -----------------------------
# Check API key
# -----------------------------

if not read_api_key:
    st.info("👈 Enter your ThingSpeak Read API Key in the sidebar.")
    st.stop()

# -----------------------------
# Get ThingSpeak data
# -----------------------------

url = (
    f"https://api.thingspeak.com/channels/"
    f"{channel_id}/feeds.json"
    f"?api_key={read_api_key}"
    f"&results={number_of_readings}"
)

try:

    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        st.error("Unable to connect to ThingSpeak.")
        st.stop()

    data = response.json()

    feeds = data.get("feeds", [])

    if not feeds:
        st.warning("No sensor data found.")
        st.stop()

    # -----------------------------
    # Convert to DataFrame
    # -----------------------------

    df = pd.DataFrame(feeds)

    df["created_at"] = pd.to_datetime(df["created_at"])

    df["Temperature"] = pd.to_numeric(
        df["field1"], errors="coerce"
    )

    df["Current"] = pd.to_numeric(
        df["field2"], errors="coerce"
    )

    df["Voltage"] = pd.to_numeric(
        df["field3"], errors="coerce"
    )

    df["Vibration"] = pd.to_numeric(
        df["field4"], errors="coerce"
    )

    df = df.dropna(
        subset=[
            "Temperature",
            "Current",
            "Voltage",
            "Vibration"
        ]
    )

    # -----------------------------
    # Latest reading
    # -----------------------------

    latest = df.iloc[-1]

    temperature = latest["Temperature"]
    current = latest["Current"]
    voltage = latest["Voltage"]
    vibration = latest["Vibration"]

    # -----------------------------
    # PredictX thresholds
    # -----------------------------

    abnormal = (
        temperature > 60
        or current > 4.0
        or voltage > 22.0
        or vibration > 8.0
    )

    # -----------------------------
    # Dashboard metrics
    # -----------------------------

    st.success("✅ ThingSpeak connected successfully")

    st.markdown("## 📊 Live Sensor Monitoring")

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
            "📳 Vibration",
            f"{vibration:.2f}"
        )

    # -----------------------------
    # Status
    # -----------------------------

    st.markdown("## 🚦 System Status")

    if abnormal:

        st.error("⚠️ ABNORMAL CONDITION DETECTED")

        if temperature > 60:
            diagnosis = "High temperature detected."
            action = "Check cooling system and temperature source."

        elif current > 4.0:
            diagnosis = "High current detected."
            action = "Check for overload or electrical fault."

        elif voltage > 22.0:
            diagnosis = "High voltage detected."
            action = "Check power supply and voltage regulation."

        elif vibration > 8.0:
            diagnosis = "High vibration detected."
            action = "Check mechanical alignment and moving components."

        else:
            diagnosis = "Abnormal sensor pattern detected."
            action = "Inspect the system."

        st.warning(f"🔎 Diagnosis: {diagnosis}")
        st.info(f"🛠️ Recommended Action: {action}")

    else:

        st.success("✅ SYSTEM OPERATING NORMALLY")
        st.write("🔎 Diagnosis: No abnormal condition detected.")
        st.write("🛠️ Recommended Action: No action required.")

    # -----------------------------
    # Sensor Charts
    # -----------------------------

    st.markdown("## 📈 Sensor Trends")

    chart_data = df[
        [
            "created_at",
            "Temperature",
            "Current",
            "Voltage",
            "Vibration"
        ]
    ].set_index("created_at")

    st.line_chart(
        chart_data[
            ["Temperature"]
        ]
    )

    st.line_chart(
        chart_data[
            ["Current"]
        ]
    )

    st.line_chart(
        chart_data[
            ["Voltage"]
        ]
    )

    st.line_chart(
        chart_data[
            ["Vibration"]
        ]
    )

    # -----------------------------
    # Recent readings
    # -----------------------------

    st.markdown("## 📋 Recent Sensor Readings")

    display_df = df[
        [
            "created_at",
            "Temperature",
            "Current",
            "Voltage",
            "Vibration"
        ]
    ].copy()

    display_df.columns = [
        "Time",
        "Temperature (°C)",
        "Current (A)",
        "Voltage (V)",
        "Vibration"
    ]

    st.dataframe(
        display_df.tail(10),
        use_container_width=True
    )

except Exception as e:

    st.error("❌ Something went wrong while loading ThingSpeak data.")

    st.write("Error:", e)
