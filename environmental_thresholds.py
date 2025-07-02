# environmental_thresholds.py

# Define the environmental thresholds for C3 plants, including updated Valve ranges
thresholds = {
    'Carbon Dioxide': {'optimal': (350, 1000), 'extreme': (150, 5000)},  # ppm
    'Photosynthetically Active Radioa': {'optimal': (200, 700), 'extreme': (0, 2000)},  # µmol/m²/s
    'Relative Humidity': {'optimal': (40, 70), 'extreme': (35, 80)},  # percent
    'Temperature': {'optimal': (18, 27), 'extreme': (0, 35)},  # °C
    'Vapor Pressure Deficit': {'optimal': (0.65, 1.25), 'extreme': (0.5, 2)},  # mbar
    'Electrical Conductivity': {'optimal': (1.0, 3.0), 'extreme': (0.5, 4)},  # mS/cm
    'Level': {'optimal': (50, 85), 'extreme': (30, 100)},  # cm (root zone moisture, solution tank level)
    'Ph Value': {'optimal': (5.5, 6.5), 'extreme': (4.0, 8.0)},  # pH
    'Pressure': {'optimal': (101, 101), 'extreme': (90, 150)},  # kPa
    'Volume': {'optimal': (50, 85), 'extreme': (30, 100)},  # liters
    'Valve': {'optimal': (19.0, 28.0), 'extreme': (14.0, 30.0)},  # control value in percentage (adjusted based on provided values)
    'Dew Point': {'optimal': (10, 15), 'extreme': (5, 20)},  # °C
    'Light Intensity': {'optimal': (150, 400), 'extreme': (0, 5000)}  # lux
}

# Define thresholds for detecting specific perturbations (patterns of anomalies)
# These are rates of change or absolute thresholds for perturbation triggers
perturbation_thresholds = {
    "co2_leak_rate": 100,  # ppm change per minute over a short period to indicate a leak
    "temperature_spike": 2,  # °C change in 10 minutes to indicate a sudden anomaly
    "light_failure_threshold": 50,  # absolute lux value below which multiple readings indicate light failure
    "humidity_swing": 10,  # % change in humidity in 30 minutes
}

# Function to get the environmental thresholds for a specific parameter
def get_threshold(parameter):
    if parameter in thresholds:
        return thresholds[parameter]
    else:
        return None  # Return None if parameter is not found

# Example usage (only runs when this file is executed directly)
if __name__ == "__main__":
    print("Environmental Thresholds:")
    for param, vals in thresholds.items():
        print(f"- {param}: Optimal {vals['optimal']}, Extreme {vals['extreme']}")
    
    print("\nPerturbation Thresholds:")
    for pert, val in perturbation_thresholds.items():
        print(f"- {pert}: {val}")