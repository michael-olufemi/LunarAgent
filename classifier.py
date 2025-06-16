import logging
from detectors import co2, temp, rh, par, vpd, light, ec, ph, level, volume, pressure, valve

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def classify(data: dict):
    sensor = data.get("sensor", "").lower()
    if sensor.startswith("co2"):
        co2.detect(data)
    elif sensor.startswith("temp"):
        temp.detect(data)
    elif sensor.startswith("rh"):
        rh.detect(data)
    elif sensor.startswith("par"):
        par.detect(data)
    elif sensor.startswith("vpd"):
        vpd.detect(data)
    elif sensor.startswith("l1") or sensor.startswith("l2") or sensor.startswith("l3") or sensor.startswith("l4"):
        light.detect(data)
    elif sensor.startswith("r1") or sensor.startswith("r2") or sensor.startswith("r3") or sensor.startswith("r4"):
        light.detect(data)  # Temporary fallback until 'reflectance.py' is defined
    elif sensor.startswith("ec"):
        ec.detect(data)
    elif sensor.startswith("ph"):
        ph.detect(data)
    elif sensor.startswith("level"):
        level.detect(data)
    elif sensor.startswith("volume"):
        volume.detect(data)
    elif sensor.startswith("pressure"):
        pressure.detect(data)
    elif sensor.startswith("valve"):
        valve.detect(data)
    else:
        logging.warning(f"⚠️ Unknown sensor type: {sensor}")