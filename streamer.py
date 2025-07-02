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
from classifier import classify

warnings.filterwarnings("ignore")

DATA_DIR = os.path.join(os.path.dirname(__file__) or ".", "data")
DROP_COLUMNS = {"Mission_Milestone"}
REALTIME_DELAY = 0.01  # seconds

def get_source(file_path):
    if "edeniss2020" in file_path.lower():
        return "edeniss2020"
    name = os.path.splitext(os.path.basename(file_path))[0]
    if "_EDA" in name:
        name = name.replace("_EDA", "")
    parts = name.split("_")
    return "_".join(parts[:2]) if len(parts) > 2 and parts[-1].isdigit() else name

def extract_events_from_file(file_path):
    events = []
    source = get_source(file_path)
    if "edeniss2020" in file_path.lower():
        subsystem = Path(file_path).parts[-2].lower()
    else:
        subsystem = None

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
                        value = int(value) if re.fullmatch(r"[-+]?\d+", value) else float(value)
                    except Exception:
                        continue

                clean_sensor = sensor.strip().rstrip(".xy").lower().replace(" ", "_")

                if source == "edeniss2020" and subsystem:
                    full_sensor_name = f"{source}-{subsystem}-{clean_sensor}"
                else:
                    full_sensor_name = f"{source}-{clean_sensor}"

                try:
                    obj = SensorData(
                        timestamp=dt, # Keep as datetime for sorting
                        sensor=full_sensor_name,
                        value=value,
                        source=source
                    )
                    events.append((dt, obj))
                except Exception as e:
                    print(f"❌ Validation error: {e}", file=sys.stderr)
    return events

async def stream_sorted_events(events):
    events.sort(key=lambda x: x[0])
    for _, sensor_obj in events:
        data = sensor_obj.dict()
        # Ensure timestamp is a string for the classifier/detector
        data['timestamp'] = data['timestamp'].strftime("%Y-%m-%dT%H:%M:%S")
        classify(data)
        await asyncio.sleep(REALTIME_DELAY)

# NEW function that can be imported by other scripts
async def stream_all_events_to_classifier(data_dir: str):
    """
    Scans a directory for CSV files, extracts sensor data, and streams it
    to the classifier in chronological order.
    """
    if not os.path.isdir(data_dir):
        print(f"❌ Data directory '{data_dir}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 Loading data from: {data_dir}")
    all_events = []

    for root, _, files in os.walk(data_dir):
        for filename in files:
            if filename.lower().endswith(".csv"):
                full_path = os.path.join(root, filename)
                all_events.extend(extract_events_from_file(full_path))
    
    if not all_events:
        print("No events found to stream.")
        return

    await stream_sorted_events(all_events)

async def main():
    """Main function to run the streamer as a standalone script."""
    # This now calls the new importable function
    await stream_all_events_to_classifier(DATA_DIR)

if __name__ == "__main__":
    asyncio.run(main())