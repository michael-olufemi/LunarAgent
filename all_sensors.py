import os
from pathlib import Path
import polars as pl
import csv

DATA_DIR = os.path.join(os.path.dirname(__file__) or ".", "data")
DROP_COLUMNS = {"Mission_Milestone"}

# Function to get source from the file path
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
    return "_".join(parts[:2]) if len(parts) > 2 and parts[-1].isdigit() else name.lower()

# Extract sensor names from files
def extract_sensor_names(file_path):
    sensors = set()
    source = get_source(file_path)

    try:
        df = pl.read_csv(file_path, ignore_errors=True)

        # Drop unnecessary columns
        for col in DROP_COLUMNS:
            if col in df.columns:
                df = df.drop(col)

        # If sensor names are in a dedicated column
        for col in df.columns:
            if col.lower() in ("sensor", "name"):
                sensors.update(f"{source}-{s}".lower() for s in df[col].unique().to_list())
                return sensors  # ✅ done

        # Otherwise assume sensors are in column headers (wide format)
        ts_col = next((c for c in df.columns if "time" in c.lower() or "date" in c.lower()), df.columns[0])
        sensor_cols = [col for col in df.columns if col != ts_col]
        for sensor in sensor_cols:
            clean = sensor.rstrip(".xy")
            sensors.add(f"{source}-{clean}".lower())
    except Exception:
        pass

    return sensors

# Load all sensors by iterating through the CSV files
def load_all_sensors():
    all_sensors = set()
    for root, _, files in os.walk(DATA_DIR):
        for filename in files:
            if filename.endswith(".csv"):
                full_path = os.path.join(root, filename)
                all_sensors.update(extract_sensor_names(full_path))
    return sorted(all_sensors)

# Load sensor mappings from the CSV file (make sure to pass the correct file)
def create_sensor_mapping(csv_file):
    sensor_mapping = {}
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Constructing the sensor identifier
            sensor_id = f"edeniss2020-{row['Path'].replace('/', '-').replace('.csv', '').lower()}"
            sensor_type_long = row['Sensor Type (long)']
            unit = row['Unit']
            
            # Mapping sensor to its general type and unit
            sensor_mapping[sensor_id] = {
                'parameter': sensor_type_long,
                'unit': unit
            }
    return sensor_mapping

# Assuming you have a file 'edeniss2020_updated.csv' with the updated sensor mapping
sensor_mapping = create_sensor_mapping('edeniss2020_updated.csv')

# Add APEX and VEG sensors
apex_sensors = {
    'apex_03-rh_percent_ground_hardware': {'parameter': 'Relative Humidity', 'unit': 'percent'},
    'apex_03-rh_percent_iss_hardware': {'parameter': 'Relative Humidity', 'unit': 'percent'},
    'apex_03-temp_degc_ground_hardware': {'parameter': 'Temperature', 'unit': 'degrees celsius'},
    'apex_03-temp_degc_iss_hardware': {'parameter': 'Temperature', 'unit': 'degrees celsius'},
    'apex_04-dewpoint_c_ground_hardware': {'parameter': 'Dew Point', 'unit': 'degrees celsius'},
    'apex_04-lux_ground_hardware': {'parameter': 'Light Intensity', 'unit': 'lux'},
    'apex_04-lux_iss_hardware': {'parameter': 'Light Intensity', 'unit': 'lux'},
    'apex_04-rh_percent_ground_hardware': {'parameter': 'Relative Humidity', 'unit': 'percent'},
    'apex_04-rh_percent_iss_hardware': {'parameter': 'Relative Humidity', 'unit': 'percent'},
    'apex_04-temp_degc_ground_hardware': {'parameter': 'Temperature', 'unit': 'degrees celsius'},
    'apex_04-temp_degc_iss_hardware': {'parameter': 'Temperature', 'unit': 'degrees celsius'}
}

veg_sensors = {
    'veg_01ab-rh_percent_ground_hardware': {'parameter': 'Relative Humidity', 'unit': 'percent'},
    'veg_01ab-rh_percent_iss_hardware': {'parameter': 'Relative Humidity', 'unit': 'percent'},
    'veg_01ab-temp_degc_ground_hardware': {'parameter': 'Temperature', 'unit': 'degrees celsius'},
    'veg_01ab-temp_degc_iss_hardware': {'parameter': 'Temperature', 'unit': 'degrees celsius'},
    'veg_01c-co2_ppm_ground_hardware': {'parameter': 'Carbon Dioxide', 'unit': 'ppm'},
    'veg_01c-co2_ppm_iss_hardware': {'parameter': 'Carbon Dioxide', 'unit': 'ppm'},
    'veg_01c-rh_percent_ground_hardware': {'parameter': 'Relative Humidity', 'unit': 'percent'},
    'veg_01c-rh_percent_iss_hardware': {'parameter': 'Relative Humidity', 'unit': 'percent'},
    'veg_01c-temp_degc_ground_hardware': {'parameter': 'Temperature', 'unit': 'degrees celsius'},
    'veg_01c-temp_degc_iss_hardware': {'parameter': 'Temperature', 'unit': 'degrees celsius'}
}

# Update sensor_mapping with APEX and VEG sensors
sensor_mapping.update(apex_sensors)
sensor_mapping.update(veg_sensors)

# Now merge the sensors and their parameters
merged_sensor_data = {}
for sensor in sensor_mapping:
    merged_sensor_data[sensor] = sensor_mapping[sensor]

