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


# Function to get the thresholds for a specific parameter
def get_threshold(parameter):
    if parameter in thresholds:
        return thresholds[parameter]
    else:
        return None  # Return None if parameter is not found

# Example usage
if __name__ == "__main__":
    print(get_threshold('Temperature'))  # Example of getting thresholds for Temperature
