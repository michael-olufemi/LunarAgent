# classifier.py
import logging
from detector import detect  # Single detect function handles all
from all_sensors import ALL_SENSORS

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Use a set for fast lookup
KNOWN_SENSORS = set(ALL_SENSORS)

def classify(data: dict):
    sensor = data.get("sensor", "").lower()

    if sensor in KNOWN_SENSORS:
        detect(data)  # 🧠 Route to detector
    else:
        logging.warning(f"⚠️ Unknown sensor type: {sensor}")
