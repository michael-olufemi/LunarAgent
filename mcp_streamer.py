import asyncio
import pandas as pd
import os
import json
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

# === CONFIG ===
ROLLING_WINDOW = 20
Z_THRESHOLD = 2.3
FREQUENCY_WINDOW_MINUTES = 10
DATA_FOLDER = "edeniss2020/ams-feg"
LOG_FILE = "anomaly_log.jsonl"

# === Data Model ===
class SensorReading(BaseModel):
    timestamp: datetime
    value: float
    sensor: str

# === MCP Logic ===
class MCPApp:
    def __init__(self):
        self.anomaly_log = []
        self.recent_anomalies = []

    def handle_anomaly(self, reading: SensorReading, z_score: float):
        now = reading.timestamp
        entry = {
            "timestamp": now.isoformat(),
            "sensor": reading.sensor,
            "value": reading.value,
            "z_score": z_score
        }
        self.anomaly_log.append(entry)
        self.recent_anomalies.append(now)

        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")

        # Frequency check
        cutoff = now - timedelta(minutes=FREQUENCY_WINDOW_MINUTES)
        self.recent_anomalies = [t for t in self.recent_anomalies if t >= cutoff]
        frequent = len(self.recent_anomalies) > 3

        # Decision logic
        if z_score > 5.0:
            action = "🚨 EMERGENCY — Shut down air system"
        elif z_score > 3.0 and frequent:
            action = "⚠️ Frequent anomalies — Increase ventilation"
        elif z_score > Z_THRESHOLD:
            action = "📋 Log anomaly — Monitor closely"
        else:
            action = "✅ Stable"

        print(f"🤖 {reading.sensor} @ {now} — {action} | z={z_score:.2f}")

# === Load Any CSV File ===
def load_csv(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df.columns = [col.strip().lower() for col in df.columns]

    # Normalize column names
    if "time" in df.columns:
        df.rename(columns={"time": "timestamp"}, inplace=True)
    if "co2-1" in df.columns:
        df.rename(columns={"co2-1": "value"}, inplace=True)
    if "co2-gl" in df.columns:
        df.rename(columns={"co2-gl": "value"}, inplace=True)
    if "value" not in df.columns:
        for candidate in df.columns:
            if candidate not in ("timestamp", "sensor"):
                df.rename(columns={candidate: "value"}, inplace=True)
                break
    if "sensor" not in df.columns:
        filename = os.path.basename(filepath).replace(".csv", "")
        df["sensor"] = filename

    return df[["timestamp", "value", "sensor"]]

# === Streaming Runner ===
async def stream_with_mcp(df: pd.DataFrame, mcp: MCPApp):
    window = []

    for _, row in df.iterrows():
        try:
            reading = SensorReading(**row.to_dict())
            window.append(reading.value)

            if len(window) > ROLLING_WINDOW:
                window.pop(0)

            if len(window) >= ROLLING_WINDOW:
                mean = sum(window) / len(window)
                std = pd.Series(window).std()
                z = (reading.value - mean) / std if std else 0

                if abs(z) > Z_THRESHOLD:
                    mcp.handle_anomaly(reading, z)
                else:
                    print(f"✅ {reading.sensor} | {reading.timestamp} — {reading.value:.2f} (z={z:.2f})")
            else:
                print(f"⏳ {reading.sensor} | {reading.timestamp} — {reading.value:.2f} (warming up...)")

        except Exception as e:
            print(f"❌ Invalid row: {row.to_dict()} — {e}")
        await asyncio.sleep(0.1)

# === Main ===
async def main():
    mcp = MCPApp()
    tasks = []

    for filename in os.listdir(DATA_FOLDER):
        if not filename.endswith(".csv"):
            continue
        path = os.path.join(DATA_FOLDER, filename)
        df = load_csv(path)
        tasks.append(asyncio.create_task(stream_with_mcp(df, mcp)))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
