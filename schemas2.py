#####to collect multiple data type and validate them
####This code processes raw input from different sensors by extracting the numeric reading as a float and, if present
####takes any trailing characters as the unit. 
####It also handles inputs that don't include units by leaving the unit field empty or using a provided one, 
####ensuring the data is consistently structured for further analysis.
from pydantic import BaseModel, root_validator
from typing import Optional
from datetime import datetime
import re

class SensorData(BaseModel):
    timestamp: datetime
    value: float
    units: Optional[str] = None
    source: Optional[str] = None  # e.g., "CO2-sensor", "humidity-sensor", etc.

    @root_validator(pre=True)
    def parse_value_and_units(cls, values):
        raw_value = values.get("value")

        if isinstance(raw_value, str):
            #match numbers with decimals and  units (e.g., "23.5 °C", "1273 ppm")
            match = re.match(r"^\s*([-+]?[0-9]*\.?[0-9]+)\s*([^\d\s]+.*)?$", raw_value)
            if match:
                number_part = float(match.group(1))
                unit_part = match.group(2).strip() if match.group(2) else None
                values["value"] = number_part
                if "units" not in values or values["units"] is None:
                    values["units"] = unit_part
        elif isinstance(raw_value, (int, float)):
            values["value"] = float(raw_value)
        else:
            raise ValueError(f"Invalid value format: {raw_value}")

        return values
