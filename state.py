from pydantic import BaseModel
from typing import List, Optional

class AgentState(BaseModel):
    farmer_id: str | None = None
    field_id: str | None = None

    field_config: dict | None = None
    iot_data: dict | None = None
    satellite_data: dict | None = None
    flood_risk: dict | None = None
    carbon_data: dict | None = None

    problems: List[str] = []
    solutions: List[str] = []

