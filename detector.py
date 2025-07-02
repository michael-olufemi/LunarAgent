import logging
from collections import defaultdict
from statistics import mean, stdev
from datetime import datetime
from environmental_thresholds import get_threshold  # Import the threshold function

# Configure logging to be less verbose. This is the main change.
# Warnings and errors will still appear, but informational messages will not fill up the console.
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    timestamp_str = data.get("timestamp") # The timestamp arrives as a string
    parameter = data.get("parameter")
    unit = data.get("unit")

    if sensor is None or value is None or parameter is None:
        return

    # --- THIS IS THE CRITICAL FIX ---
    # Convert the timestamp string from the streamer back into a datetime object.
    # This ensures that a proper datetime object is stored in the ANOMALY_LOG.
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
    except (ValueError, TypeError):
        logger.warning(f"Could not parse timestamp string from streamer: {timestamp_str}")
        return
    # ---------------------------------

    # Append value to SENSOR_HISTORY at the start of detection
    SENSOR_HISTORY[sensor].append(value)

    # Log current history length for debugging
    logger.debug(f"Checking Z-score for sensor {sensor} | Current data length: {len(SENSOR_HISTORY[sensor])}")

    # Normalize parameter for uniformity (capitalize each word and strip spaces)
    parameter = parameter.strip().title()

    # Fetch parameter thresholds from environmental thresholds
    thresholds = get_threshold(parameter)
    if thresholds is None:
        logger.error(f"❌ No thresholds found for parameter: {parameter}")
        return

    # Unpack thresholds
    optimal_min, optimal_max = thresholds['optimal']
    extreme_min, extreme_max = thresholds['extreme']

    anomaly_detected = False
    anomaly_details = {}

    # Threshold-based anomaly detection
    if value < extreme_min or value > extreme_max:
        anomaly_detected = True
        anomaly_details = {
            "threshold_type": "extreme",
            "threshold": (extreme_min, extreme_max),
        }
    elif value < optimal_min or value > optimal_max:
        anomaly_detected = True
        anomaly_details = {
            "threshold_type": "optimal",
            "threshold": (optimal_min, optimal_max),
        }

    if anomaly_detected:
        anomaly = {
            "sensor": sensor, "parameter": parameter, "unit": unit, "value": value,
            "timestamp": timestamp, # Now appending the correct datetime object
            **anomaly_details
        }
        logger.info(f"Threshold Anomaly: {anomaly_details['threshold_type']} for {sensor}")
        ANOMALY_LOG.append(anomaly)

    # Calculate Z-score for each new value as data streams in
    values = SENSOR_HISTORY[sensor]
    if len(values) >= MIN_HISTORY:
        try:
            mu = mean(values)
            sigma = stdev(values)

            if sigma != 0:
                z = (value - mu) / sigma
                if abs(z) > THRESHOLD_Z:
                    z_anomaly = {
                        "sensor": sensor, "parameter": parameter, "unit": unit, "value": value,
                        "z_score": round(z, 2), "timestamp": timestamp, "threshold_type": "z_score"
                    }
                    logger.info(f"Z-Score Anomaly for {sensor}")
                    ANOMALY_LOG.append(z_anomaly)
            else:
                logger.debug(f"Insufficient data (sigma == 0) for Z-score on {sensor}")
        except Exception as e:
            logger.error(f"Error calculating Z-score for {sensor}: {e}")

    # Trend-based detection for anomaly (rate of change detection)
    rate_of_change = calculate_rate_of_change(values)
    if abs(rate_of_change) > THRESHOLD_RATE:
        trend_anomaly = {
            "sensor": sensor, "parameter": parameter, "unit": unit, "value": value,
            "rate_of_change": rate_of_change, "timestamp": timestamp, "threshold_type": "trend"
        }
        logger.info(f"Trend Anomaly for {sensor}")
        ANOMALY_LOG.append(trend_anomaly)