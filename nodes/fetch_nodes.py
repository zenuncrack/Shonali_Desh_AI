# nodes/fetch_nodes.py

from state import AgentState
from tools.firebase_tools import fetch_field_config_tool, fetch_iot_data_tool
from tools.satellite_tools import fetch_satellite_tool
from tools.flood_tools import fetch_flood_risk_tool
from tools.carbon_tools import fetch_carbon_from_ndvi


# ---------------------------------------------------------
# 1. Fetch Farmer + Field Config
# ---------------------------------------------------------
def node_fetch_field_and_farmer(state: AgentState) -> AgentState:
    state.field_config = fetch_field_config_tool.invoke({
        "farmer_id": state.farmer_id,
        "field_id": state.field_id,
    })
    return state


# ---------------------------------------------------------
# 2. Fetch IoT Sensor Data
# ---------------------------------------------------------
def node_fetch_iot(state: AgentState) -> AgentState:
    state.iot_data = fetch_iot_data_tool.invoke({
        "farmer_id": state.farmer_id,
        "field_id": state.field_id,
    })
    return state


# ---------------------------------------------------------
# 3. Fetch Satellite Data
# ---------------------------------------------------------
def node_fetch_satellite(state: AgentState) -> AgentState:
    cfg = state.field_config or {}
    loc = cfg.get("location", {}) if isinstance(cfg, dict) else {}

    state.satellite_data = fetch_satellite_tool.invoke({
        "lat": loc.get("lat"),
        "lon": loc.get("lon"),
    })

    return state


# ---------------------------------------------------------
# 4. Fetch Carbon Sequestration (NEW)
# ---------------------------------------------------------
def node_fetch_carbon(state: AgentState) -> AgentState:
    cfg = state.field_config or {}
    loc = cfg.get("location", {}) if isinstance(cfg, dict) else {}

    lat = loc.get("lat")
    lon = loc.get("lon")

    if lat is None or lon is None:
        state.carbon_data = None
        return state

    state.carbon_data = fetch_carbon_from_ndvi.invoke({
        "lat": lat,
        "lon": lon,
        "area_ha": 1.0
    })

    return state


# ---------------------------------------------------------
# 5. Fetch Flood Risk
# ---------------------------------------------------------
def node_fetch_flood(state: AgentState) -> AgentState:
    cfg = state.field_config or {}
    loc = cfg.get("location", {}) if isinstance(cfg, dict) else {}

    state.flood_risk = fetch_flood_risk_tool.invoke({
        "lat": loc.get("lat"),
        "lon": loc.get("lon"),
    })

    return state
