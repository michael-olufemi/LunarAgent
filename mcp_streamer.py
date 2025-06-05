import asyncio
import pandas as pd
import json
from datetime import datetime, timedelta
from pydantic import BaseModel, validator

# === Parameters ===
ROLLING_WINDOW = 20
Z_THRESHOLD = 2.3
FREQUENCY_WINDOW_MINUTES = 10
LOG_FILE = "anomaly_log.jsonl"

# === Pydantic Schema for Validation ===
class CO2Reading(BaseModel):
    timestamp: datetime
    co2_ppm: float

    @validator("co2_ppm")
    def co2_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("CO₂ must be a positive number")
        return v

# === MCPApp with File Logging ===
class MCPApp:
    def __init__(self):
        self.anomaly_log = []
        self.recent_anomalies = []

    def handle_anomaly(self, reading: CO2Reading, z_score: float):
        now = reading.timestamp
        entry = {
            "timestamp": now.isoformat(),
            "co2_ppm": reading.co2_ppm,
            "z_score": z_score
        }
        self.anomaly_log.append(entry)
        self.recent_anomalies.append(now)

        # Save to file
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")

        # Frequency logic
        cutoff = now - timedelta(minutes=FREQUENCY_WINDOW_MINUTES)
        self.recent_anomalies = [t for t in self.recent_anomalies if t >= cutoff]
        frequent = len(self.recent_anomalies) > 3

        # Decision logic
        if z_score > 5.0:
            action = "🚨 EMERGENCY — Shut down air system"
        elif z_score > 3.0 and frequent:
            action = "⚠️ Frequent anomalies — Increase ventilation"
        elif z_score > 2.3:
            action = "📋 Log anomaly — Monitor closely"
        else:
            action = "✅ Stable"

        print(f"🤖 MCPApp: {action} | z={z_score:.2f} | Time: {now}")

# === Load Data ===
def load_data(filepath):
    df = pd.read_csv(filepath)
    df.rename(columns={"time": "timestamp", "co2-1": "co2_ppm"}, inplace=True)
    return df

# === Streamer ===
async def stream_with_mcp(df, mcp_app):
    window = []

    for _, row in df.iterrows():
        try:
            reading = CO2Reading(timestamp=row["timestamp"], co2_ppm=row["co2_ppm"])
            window.append(reading.co2_ppm)

            if len(window) > ROLLING_WINDOW:
                window.pop(0)

            if len(window) >= ROLLING_WINDOW:
                mean = sum(window) / len(window)
                std = pd.Series(window).std()
                z = (reading.co2_ppm - mean) / std if std else 0

                if abs(z) > Z_THRESHOLD:
                    print(f"🚨 Anomaly at {reading.timestamp} — CO₂: {reading.co2_ppm:.1f} ppm (z={z:.2f})")
                    mcp_app.handle_anomaly(reading, z)
                else:
                    print(f"✅ {reading.timestamp} — CO₂: {reading.co2_ppm:.1f} ppm (z={z:.2f})")
            else:
                print(f"⏳ {reading.timestamp} — CO₂: {reading.co2_ppm:.1f} ppm (warming up...)")

        except Exception as e:
            print(f"❌ Invalid row: {row.to_dict()} — {e}")

        await asyncio.sleep(0.1)

# === Main ===
if __name__ == "__main__":
    file_path = "/Users/michaelolufemi/Documents/Lunar_Agent/edeniss2020/ams-feg/co2-1.csv"
    df = load_data(file_path)
    mcp = MCPApp()
    asyncio.run(stream_with_mcp(df, mcp))
