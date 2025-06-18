# all_sensors.py
import os
from pathlib import Path
import polars as pl

DATA_DIR = os.path.join(os.path.dirname(__file__) or ".", "data")
DROP_COLUMNS = {"Mission_Milestone"}

def get_source(file_path):
    path = Path(file_path)
    if "edeniss2020" in file_path.lower():
        parts = path.parts
        if "edeniss2020" in parts:
            idx = parts.index("edeniss2020")
            return f"edeniss2020-{parts[idx + 1].lower()}" if len(parts) > idx + 1 else "edeniss2020"
        return "edeniss2020"
    name = os.path.splitext(os.path.basename(file_path))[0]
    if "_EDA" in name:
        name = name.replace("_EDA", "")
    parts = name.split("_")
    return "_".join(parts[:2]).lower() if len(parts) > 2 and parts[-1].isdigit() else name.lower()

def extract_sensor_names(file_path):
    sensors = set()
    source = get_source(file_path)

    try:
        df = pl.read_csv(file_path, ignore_errors=True)

        for col in DROP_COLUMNS:
            if col in df.columns:
                df = df.drop(col)

        ts_col = next((c for c in df.columns if "time" in c.lower() or "date" in c.lower()), df.columns[0])
        sensor_cols = [col for col in df.columns if col != ts_col]

        for sensor in sensor_cols:
            clean = sensor.rstrip(".xy")
            sensors.add(f"{source}-{clean}".lower())  # normalize to lowercase
    except Exception:
        pass

    return sensors

def load_all_sensors():
    all_sensors = set()
    for root, _, files in os.walk(DATA_DIR):
        for filename in files:
            if filename.endswith(".csv"):
                full_path = os.path.join(root, filename)
                all_sensors.update(extract_sensor_names(full_path))
    return sorted(all_sensors)

# Export this list as a module variable
ALL_SENSORS = load_all_sensors()


