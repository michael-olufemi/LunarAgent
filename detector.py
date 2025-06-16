# This module contains all the sensor-specific detector logic.
# Each file corresponds to a sensor type (e.g., co2.py, temp.py), and exports a `detect(data)`
# function that checks whether the sensor value is within a normal range or triggers an alert.

def detect(data):
    value = data.get("value")
    if value is None:
        return
    if value < 300:
        print(f"[CO2] LOW: {value} ppm")
    elif value > 1200:
        print(f"[CO2] HIGH: {value} ppm")
    else:
        print(f"[CO2] Normal: {value} ppm")


# detectors/temp.py
def detect(data):
    value = data.get("value")
    if value is None:
        return
    if value < 18:
        print(f"[TEMP] TOO COLD: {value} °C")
    elif value > 30:
        print(f"[TEMP] TOO HOT: {value} °C")
    else:
        print(f"[TEMP] Normal: {value} °C")


# detectors/rh.py
def detect(data):
    value = data.get("value")
    if value is None:
        return
    if value < 40:
        print(f"[RH] TOO DRY: {value}%")
    elif value > 70:
        print(f"[RH] TOO HUMID: {value}%")
    else:
        print(f"[RH] Normal: {value}%")


# detectors/par.py
def detect(data):
    value = data.get("value")
    if value is None:
        return
    if value < 200:
        print(f"[PAR] TOO LOW: {value} µmol/m2/s")
    elif value > 800:
        print(f"[PAR] TOO HIGH: {value} µmol/m2/s")
    else:
        print(f"[PAR] Normal: {value} µmol/m2/s")


# detectors/light.py
def detect(data):
    print(f"[LIGHT ZONE] Sensor: {data['sensor']}, Value: {data['value']}")


# detectors/vpd.py
def detect(data):
    value = data.get("value")
    if value is None:
        return
    if value < 0.4:
        print(f"[VPD] TOO LOW: {value} kPa")
    elif value > 1.5:
        print(f"[VPD] TOO HIGH: {value} kPa")
    else:
        print(f"[VPD] Normal: {value} kPa")


# detectors/ec.py
def detect(data):
    value = data.get("value")
    if value is None:
        return
    if value < 1.2:
        print(f"[EC] TOO LOW: {value} mS/cm")
    elif value > 2.4:
        print(f"[EC] TOO HIGH: {value} mS/cm")
    else:
        print(f"[EC] Normal: {value} mS/cm")


# detectors/ph.py
def detect(data):
    value = data.get("value")
    if value is None:
        return
    if value < 5.5:
        print(f"[pH] TOO ACIDIC: {value}")
    elif value > 6.5:
        print(f"[pH] TOO ALKALINE: {value}")
    else:
        print(f"[pH] Normal: {value}")


# detectors/level.py
def detect(data):
    value = data.get("value")
    if value is None:
        return
    if value < 20:
        print(f"[LEVEL] LOW WATER: {value}%")
    else:
        print(f"[LEVEL] Normal: {value}%")


# detectors/volume.py
def detect(data):
    value = data.get("value")
    if value is None:
        return
    print(f"[VOLUME] Current: {value} L")


# detectors/pressure.py
def detect(data):
    value = data.get("value")
    if value is None:
        return
    if value < 0.8:
        print(f"[PRESSURE] TOO LOW: {value} bar")
    elif value > 2.5:
        print(f"[PRESSURE] TOO HIGH: {value} bar")
    else:
        print(f"[PRESSURE] Normal: {value} bar")


# detectors/valve.py
def detect(data):
    state = data.get("value")
    if state not in ["open", "closed"]:
        print(f"[VALVE] Invalid state: {state}")
    else:
        print(f"[VALVE] {data['sensor']}: {state.upper()}")
