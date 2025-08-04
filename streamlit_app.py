# app.py
import streamlit as st
import json

# --- Imports ---
import os
import json
import pandas as pd
from datetime import datetime
import streamlit as st
from chat_agent import ChatAgent
from autonomous_decision_agent import AutonomousDecisionAgent
from detector import ANOMALY_LOG

st.set_page_config(page_title="Lunar Agent Dashboard", layout="wide")
st.title("🌕 Lunar Agriculture Pod Agent Dashboard")

tabs = st.tabs([
    "📋 Agent Decisions",
    "📈 Anomaly Log",
    "🧠 Decision History",
    "💬 Chat with MCPAgent",
    "📊 Sensor Visualizer"
])

# --- Agent Decisions Tab ---
with tabs[0]:
    st.subheader("📋 Latest Decision Output")
    if st.button("🔄 Refresh", key="refresh_decision"):
        st.rerun()
    decision_file = "data/last_decision.json"
    if os.path.exists(decision_file):
        with open(decision_file, "r") as f:
            decision = json.load(f)
        st.markdown("### REASONING")
        st.info(decision.get("reasoning", "No reasoning provided."))
        st.markdown("### RESPONSE PLAN")
        st.success(decision.get("response_plan", "No plan provided."))
        st.caption(f"🕒 Last updated: {decision.get('timestamp', 'unknown')}")
        if "CRITICAL" in decision.get("raw_output", "").upper():
            st.error("🚨 CRITICAL URGENCY DETECTED!")
    else:
        st.warning("No decision output file found. Start the agent service to generate decisions.")

# --- Anomaly Log Tab ---
with tabs[1]:
    st.subheader("📈 Anomaly Log")
    if st.button("🔄 Refresh", key="refresh_anomaly"):
        st.rerun()
    found_log = False
    for path in ANOMALY_LOG:
        if os.path.exists(path):
            found_log = True
            st.markdown(f"### Log File: `{os.path.basename(path)}`")
            with open(path, 'r') as f:
                rows = [json.loads(line) for line in f.readlines()]
                df = pd.DataFrame(rows)
                if not df.empty:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601', errors='coerce')
                    df.sort_values('timestamp', ascending=False, inplace=True)
                    st.dataframe(df)
                    if 'value' in df.columns:
                        st.line_chart(df.set_index('timestamp')['value'])
                else:
                    st.info("This anomaly log is empty.")
        else:
            st.warning(f"Log file not found: {path}")
    if not found_log:
        st.warning("No anomaly log found.")

# --- Decision History Tab ---
with tabs[2]:
    st.subheader("🧠 Decision History")
    if st.button("🔄 Refresh", key="refresh_history"):
        st.rerun()
    decision_log = "data/last_decision.jsonl"
    if os.path.exists(decision_log):
        with open(decision_log, "r") as f:
            entries = [json.loads(line) for line in f.readlines()]
            df = pd.DataFrame(entries)
            if not df.empty:
                df["timestamp"] = pd.to_datetime(df["timestamp"], format='ISO8601', errors='coerce')
                df.sort_values("timestamp", ascending=False, inplace=True)
                st.dataframe(df)
            else:
                st.info("Decision history is empty.")
    else:
        st.warning("No decision history file found.")

# --- Chat Agent Tab ---
import time
with tabs[3]:
    st.subheader("💬 Chat with MCPAgent")
    agent = ChatAgent()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "animated_until" not in st.session_state:
        st.session_state.animated_until = len(st.session_state.chat_history) - 1
    history = st.session_state.chat_history
    for i, msg in enumerate(history):
        # Only animate the latest assistant message if it hasn't been animated yet
        if (
            msg["role"] == "assistant"
            and i == len(history) - 1
            and st.session_state.animated_until < i
        ):
            paragraphs = msg["content"].split('\n')
            placeholder = st.empty()
            full_text = ""
            for para in paragraphs:
                words = para.split()
                para_buffer = ""
                for word in words:
                    para_buffer += word + " "
                    display_text = (full_text + para_buffer).replace("\n", "  \n")
                    placeholder.markdown(display_text)
                    time.sleep(0.05)
                full_text += para_buffer + "\n"
            placeholder.markdown(full_text.replace("\n", "  \n"))
            st.session_state.animated_until = i
        else:
            st.chat_message(msg["role"]).markdown(msg["content"].replace("\n", "  \n"))
    # User input box below response
    prompt = st.chat_input("Ask the agent something...", key="chat_input")
    if prompt:
        st.chat_message("user").write(prompt)
        thinking_placeholder = st.empty()
        thinking_placeholder.info("⏳ Thinking...")
        response = agent.chat(prompt)
        thinking_placeholder.empty()
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.session_state.animated_until = len(st.session_state.chat_history) - 2
        st.rerun()

# --- Sensor Visualizer Tab ---
with tabs[4]:
    st.subheader("📊 Explore Sensor Data from edeniss2020")
    if st.button("🔄 Refresh", key="refresh_sensor"):
        st.rerun()
    DATA_ROOT = "/Users/ora/Documents/NASA-internship/template_michael/LunarAgent/data/edeniss2020"
    subsystems = [d for d in os.listdir(DATA_ROOT) if os.path.isdir(os.path.join(DATA_ROOT, d))]
    subsystem = st.selectbox("Select Subsystem", subsystems)
    selected_path = os.path.join(DATA_ROOT, subsystem)
    csv_files = [f for f in os.listdir(selected_path) if f.endswith(".csv") and not f.startswith("._")]
    if csv_files:
        selected_csv = st.selectbox("Select Sensor File", csv_files)
        full_path = os.path.join(selected_path, selected_csv)
        try:
            df = pd.read_csv(full_path)
            st.write("Raw Data Preview", df.head())
            # Try to parse datetime and plot
            time_col = None
            for col in df.columns:
                if "time" in col.lower() or "timestamp" in col.lower():
                    time_col = col
                    break
            if time_col:
                df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
                df = df.dropna(subset=[time_col])
                df.set_index(time_col, inplace=True)
                value_cols = df.select_dtypes(include=["float", "int"]).columns.tolist()
                if value_cols:
                    st.line_chart(df[value_cols])
                else:
                    st.warning("No numeric columns to plot.")
            else:
                st.warning("No timestamp column found to plot time series.")
        except Exception as e:
            st.error(f"Failed to read or plot CSV: {e}")
    else:
        st.info("No CSV files found in selected subsystem.")