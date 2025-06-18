Lunar Agriculture Sensor Anomaly Detector 🌱🌕

This project implements a **modular and extensible anomaly detection system** for environmental sensor data collected from space agriculture experiments (e.g., EDEN ISS, VEGGIE, APEX).

### 🚀 Overview

The system simulates real-time data streaming and performs **per-sensor anomaly detection** using a simple but effective **z-score method**. It is designed to serve as the foundation for an autonomous AI agent that monitors telemetry from a lunar greenhouse.

---

### 🧠 Core Features

- ✅ Modular architecture (streamer → classifier → detector)
- ✅ Real-time simulation using Polars + asyncio
- ✅ Anomaly detection based on per-sensor z-score
- ✅ Automatically extracts and classifies all unique sensors
- ✅ Designed to integrate easily with LLMs or visualization agents
