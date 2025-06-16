from pydantic import BaseModel
from datetime import datetime

class SensorData(BaseModel):
    timestamp: datetime
    sensor: str
    value: float
    source: str
