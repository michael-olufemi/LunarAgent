import logging
from collections import defaultdict
from statistics import mean, stdev
from datetime import datetime
from environmental_thresholds import get_threshold  # Import the threshold function

SENSOR_HISTORY = defaultdict(list)
ANOMALY_LOG = []
THRESHOLD_Z = 3.5  # More stringent Z-score threshold
MIN_HISTORY = 20   # Minimum history to start Z-score calculation (Optional for streaming)
THRESHOLD_RATE = 0.5  # Rate of change threshold for trend analysis

# Calculate rate of change for trend-based anomaly detection
def calculate_rate_of_change(sensor_data):
    if len(sensor_data) < 2:
        return 0  # Not enough data to calculate rate of change
    last_value = sensor_data[-2]
    current_value = sensor_data[-1]
    rate_of_change = current_value - last_value
    return rate_of_change

# Detect anomalies
def detect(data: dict):
    sensor = data.get("sensor")
    value = data.get("value")
    timestamp = data.get("timestamp")
    parameter = data.get("parameter")  # Assuming the parameter is part of the data
    unit = data.get("unit")  # Ensure unit is also passed

    if sensor is None or value is None or parameter is None:
        return

    # Append value to SENSOR_HISTORY at the start of detection
    SENSOR_HISTORY[sensor].append(value)

    # Log current history length for debugging
    logging.debug(f"Checking Z-score for sensor {sensor} | Current data length: {len(SENSOR_HISTORY[sensor])}")

    # Normalize parameter for uniformity (capitalize each word and strip spaces)
    parameter = parameter.strip().title()  # Or use .lower() to make everything lowercase

    # Fetch parameter thresholds from environmental thresholds
    thresholds = get_threshold(parameter)
    if thresholds is None:
        logging.error(f"❌ No thresholds found for parameter: {parameter}")
        return

    # Unpack thresholds
    optimal_min, optimal_max = thresholds['optimal']
    extreme_min, extreme_max = thresholds['extreme']

    # Threshold-based anomaly detection
    if value < extreme_min or value > extreme_max:
        anomaly_type = "extreme"
        anomaly = {
            "sensor": sensor,
            "parameter": parameter,
            "unit": unit,
            "value": value,
            "threshold_type": anomaly_type,
            "threshold": (extreme_min, extreme_max),
            "timestamp": timestamp
        }
        logging.warning(f"🚨 Extreme Anomaly: Sensor: {sensor} | {parameter}={value} | {timestamp}")
        ANOMALY_LOG.append(anomaly)

    elif value < optimal_min or value > optimal_max:
        anomaly_type = "optimal"
        anomaly = {
            "sensor": sensor,
            "parameter": parameter,
            "unit": unit,
            "value": value,
            "threshold_type": anomaly_type,
            "threshold": (optimal_min, optimal_max),
            "timestamp": timestamp
        }
        logging.warning(f"⚠️ Optimal Anomaly: Sensor: {sensor} | {parameter}={value} | {timestamp}")
        ANOMALY_LOG.append(anomaly)

    # Calculate Z-score for each new value as data streams in
    values = SENSOR_HISTORY[sensor]
    if len(values) >= MIN_HISTORY:  # Optional: Keep it here or calculate without this check
        try:
            mu = mean(values)  # Mean of the accumulated values
            sigma = stdev(values)  # Standard deviation of the accumulated values

            if sigma != 0:  # Ensure the standard deviation isn't zero
                z = (value - mu) / sigma  # Z-score formula
                if abs(z) > THRESHOLD_Z:
                    anomaly = {
                        "sensor": sensor,
                        "parameter": parameter,
                        "unit": unit,
                        "value": value,
                        "z_score": round(z, 2),
                        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S") if isinstance(timestamp, datetime) else str(timestamp),
                        "mean": round(mu, 2),
                        "std": round(sigma, 2)
                    }
                    logging.warning(f"🚨 Z-Score Anomaly: Sensor: {sensor} | {parameter}={value} | Z-Score={round(z, 2)} | {timestamp}")
                    ANOMALY_LOG.append(anomaly)
            else:
                logging.warning(f"❌ Insufficient data (sigma == 0) to calculate Z-score for sensor {sensor}. All values are the same.")
        except Exception as e:
            logging.error(f"❌ Error calculating Z-score for {sensor}: {e}")

    # Trend-based detection for anomaly (rate of change detection)
    rate_of_change = calculate_rate_of_change(SENSOR_HISTORY[sensor])
    if abs(rate_of_change) > THRESHOLD_RATE:
        anomaly = {
            "sensor": sensor,
            "parameter": parameter,
            "unit": unit,
            "value": value,
            "rate_of_change": rate_of_change,
            "timestamp": timestamp
        }
        logging.warning(f"🚨 Trend Anomaly: Sensor: {sensor} | {parameter}={value} | Rate of Change={rate_of_change} | {timestamp}")
        ANOMALY_LOG.append(anomaly)

    # Store the value for historical analysis
    SENSOR_HISTORY[sensor].append(value)
