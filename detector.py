import logging
from collections import defaultdict
from statistics import mean, stdev
from datetime import datetime

SENSOR_HISTORY = defaultdict(list)
ANOMALY_LOG = []
THRESHOLD_Z = 3.5  # More stringent
MIN_HISTORY = 20   # Require more values before anomaly detection

def detect(data: dict):
    sensor = data.get("sensor")
    value = data.get("value")
    timestamp = data.get("timestamp")

    if sensor is None or value is None:
        return

    SENSOR_HISTORY[sensor].append(value)

    if len(SENSOR_HISTORY[sensor]) < MIN_HISTORY:
        return

    values = SENSOR_HISTORY[sensor]
    try:
        mu = mean(values)
        sigma = stdev(values)
        if sigma == 0:
            return

        z = (value - mu) / sigma
        if abs(z) > THRESHOLD_Z:
            anomaly = {
                "sensor": sensor,
                "value": value,
                "z_score": round(z, 2),
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S") if isinstance(timestamp, datetime) else str(timestamp),
                "mean": round(mu, 2),
                "std": round(sigma, 2)
            }
            logging.warning(f"🚨 Anomaly: {anomaly}")
            ANOMALY_LOG.append(anomaly)

    except Exception as e:
        logging.error(f"❌ Error processing {sensor}: {e}")
