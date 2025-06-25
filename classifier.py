import logging
from detector import detect  # Single detect function handles all
from all_sensors import merged_sensor_data

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def classify(data: dict):
    sensor = data.get("sensor", "").lower()

    if sensor in merged_sensor_data:
        # Add parameter to data for threshold detection
        data["parameter"] = merged_sensor_data[sensor]["parameter"]
        data["unit"] = merged_sensor_data[sensor]["unit"]
        detect(data)  # 🧠 Route to detector
    else:
        logging.warning(f"⚠️ Unknown sensor type: {sensor}")
