#!/usr/bin/env python3
import os
import sys
import json
import warnings
import re
from pathlib import Path
from dateutil import parser
import polars as pl
import asyncio
from schemas import SensorData
from classifier import classify  # Add this import at the top

warnings.filterwarnings("ignore")

# Define the directory where Eden data is stored
DATA_DIR = os.path.join(os.path.dirname(__file__) or ".", "data", "edeniss2020")
DROP_COLUMNS = {"Mission_Milestone"}
REALTIME_DELAY = 0.0000000000001  # seconds

def get_source(file_path):
    # We only process the Eden dataset
    if "edeniss2020" in file_path.lower():
        return "edeniss2020"
    return None
def extract_events_from_file(file_path):
    events = []

    # Determine top-level data source (e.g. 'edeniss2020')
    source = get_source(file_path)

    # Determine subsystem for edeniss2020, e.g., 'ams-feg'
    if "edeniss2020" in file_path.lower():
        subsystem = Path(file_path).parts[-2].lower()
    else:
        subsystem = None  # not needed for APEX/VEG

    header_skip = 0
    try:
        with open(file_path, 'r', errors='ignore') as f:
            first, second = f.readline(), f.readline()
            if second and len(re.findall(r"[A-Za-z]", first)) < len(re.findall(r"[A-Za-z]", second)):
                header_skip = 1
    except Exception:
        return events

    try:
        df_preview = pl.read_csv(
            file_path, skip_rows=header_skip, n_rows=5,
            has_header=True, infer_schema_length=0, ignore_errors=True
        )
    except Exception:
        try:
            df_preview = pl.read_csv(
                file_path, skip_rows=header_skip, n_rows=6,
                has_header=False, ignore_errors=True
            )
            new_cols = [str(x) for x in df_preview.row(0)]
            df_preview = df_preview[1:]
            df_preview.columns = new_cols
        except Exception:
            return events

    columns = df_preview.columns
    ts_col = next((c for c in columns if "time" in c.lower() or "date" in c.lower()), columns[0])

    offset = header_skip
    batch_size = 10000
    while True:
        try:
            df = pl.read_csv(
                file_path, skip_rows=offset, n_rows=batch_size,
                has_header=(offset == header_skip),
                infer_schema_length=100, ignore_errors=True
            )
        except Exception:
            break
        if df.is_empty():
            break
        offset += df.height

        for col in DROP_COLUMNS:
            if col in df.columns:
                df = df.drop(col)

        if ts_col not in df.columns:
            fallback_cols = [c for c in df.columns if "time" in c.lower() or "date" in c.lower()]
            if fallback_cols:
                ts_col = fallback_cols[0]
            else:
                continue

        if df[ts_col].dtype != pl.Utf8:
            df = df.with_columns(pl.col(ts_col).cast(pl.Utf8))

        for row in df.iter_rows(named=True):
            ts_val = row.get(ts_col)
            if ts_val is None or str(ts_val).strip() == "":
                continue
            try:
                dt = parser.parse(str(ts_val), dayfirst=False)
            except Exception:
                continue
            ts_str = dt.strftime("%Y-%m-%dT%H:%M:%S")

            for sensor, value in row.items():
                if sensor == ts_col or value is None or (isinstance(value, str) and value.strip() == ""):
                    continue
                if isinstance(value, str):
                    try:
                        # Attempt to convert to a float first, then to an integer if possible
                        value = float(value) if re.match(r"^\d+(\.\d+)?$", value) else str(value)
                    except Exception:
                        continue

                clean_sensor = sensor.strip().rstrip(".xy").lower().replace(" ", "_")

                # ✅ CONDITIONAL NAMING LOGIC
                if source == "edeniss2020" and subsystem:
                    full_sensor_name = f"{source}-{subsystem}-{clean_sensor}"
                else:
                    full_sensor_name = f"{source}-{clean_sensor}"

                try:
                    obj = SensorData(
                        timestamp=ts_str,
                        sensor=full_sensor_name,
                        value=value,
                        source=source
                    )
                    events.append((dt, obj))
                except Exception as e:
                    print(f"❌ Validation error: {e}", file=sys.stderr)
    return events


async def stream_sorted_events(events):
    events.sort(key=lambda x: x[0])  # Sort by datetime
    for _, sensor_obj in events:
        data = sensor_obj.dict()     # Convert Pydantic object to dict
        classify(data)               # Send to classifier
        await asyncio.sleep(REALTIME_DELAY)

async def main():
    if not os.path.isdir(DATA_DIR):
        print(f"❌ Eden data directory '{DATA_DIR}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 Loading Eden data from: {DATA_DIR}")
    all_events = []

    # Scan for CSV files in edeniss2020 directory only
    for root, _, files in os.walk(DATA_DIR):
        for filename in files:
            if filename.lower().endswith(".csv"):
                full_path = os.path.join(root, filename)
                all_events.extend(extract_events_from_file(full_path))

    if not all_events:
        print("❌ No Eden events found to stream.")
        return

    await stream_sorted_events(all_events)

if __name__ == "__main__":
    asyncio.run(main())
