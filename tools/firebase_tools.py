# tools/firebase_tools.py

import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from langchain_core.tools import tool
from config.settings import FIREBASE_CRED_PATH, DEMO_MODE


# -------------------------------------------------------------------
# 0. Initialize Firebase (Realtime Database)
# -------------------------------------------------------------------

if not DEMO_MODE:
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CRED_PATH)

        firebase_admin.initialize_app(
            cred,
            {
                "databaseURL": "https://shonali-desh-19ead-default-rtdb.firebaseio.com/"
            },
        )

    print("🔥 Realtime Database initialized")
else:
    print("⚙ DEMO_MODE ON — Firebase will not be used")


# -------------------------------------------------------------------
# Utility
# -------------------------------------------------------------------

def rtdb_get(path):
    ref = db.reference(path)
    return ref.get()


def rtdb_set(path, data):
    ref = db.reference(path)
    ref.set(data)


def rtdb_push(path, data):
    ref = db.reference(path)
    return ref.push(data).key


# -------------------------------------------------------------------
# 1. Fetch Farmer + Field Config
# -------------------------------------------------------------------

@tool
def fetch_field_config_tool(farmer_id: str, field_id: str):
    """Fetch farmer + field + crop + location + prediction from Realtime DB."""

    if DEMO_MODE:
        return {
            "farmer_id": farmer_id,
            "field_id": field_id,
            "farmer_name": "Rahim",
            "cropType": "Rice",
            "location": {"lat": 23.50, "lon": 90.30},
            "debug": {"source": "DEMO_MODE"},
        }

    print("🔍 Fetching from RTDB:", farmer_id, field_id)

    farmer_path = f"Farmers/{farmer_id}"
    farmer = rtdb_get(farmer_path)

    if farmer is None:
        return {
            "error": "farmer_not_found",
            "farmer_id": farmer_id,
            "debug": f"RTDB path checked: {farmer_path}",
        }

    field_path = f"Farmers/{farmer_id}/Fields/{field_id}"
    field = rtdb_get(field_path)

    if field is None:
        return {
            "error": "field_not_found",
            "farmer_id": farmer_id,
            "field_id": field_id,
            "debug": f"RTDB path checked: {field_path}",
        }

    return {
        "farmer_id": farmer_id,
        "field_id": field_id,
        "farmer_name": farmer.get("name"),
        "phone": farmer.get("phone"),
        "region": farmer.get("region"),
        "district": farmer.get("district"),
        "upazila": farmer.get("upazila"),
        "village": farmer.get("village"),
        "fieldSize": field.get("fieldSize"),
        "cropType": field.get("cropType"),
        "soilType": field.get("soilType"),
        "location": field.get("location"),
        "currentCrop": field.get("currentCrop"),
        "latestPrediction": field.get("latestPrediction"),
    }


# -------------------------------------------------------------------
# 2. Fetch IoT Sensor Data
# -------------------------------------------------------------------

@tool
def fetch_iot_data_tool(farmer_id: str, field_id: str):
    """Fetch IoT sensor data from Realtime DB."""

    if DEMO_MODE:
        return {
            "has_data": True,
            "latest": {"soilTemp": 30, "soilMoisture": 18},
            "recent": [],
        }

    readings_path = f"Farmers/{farmer_id}/Fields/{field_id}/IoT/SensorReadings"
    readings = rtdb_get(readings_path)

    if readings is None:
        return {"has_data": False, "message": "No IoT readings found"}

    # Convert dict to sorted list (reverse chronological)
    sorted_readings = sorted(
        readings.values(),
        key=lambda x: x.get("timestamp", ""),
        reverse=True,
    )

    return {
        "has_data": True,
        "latest": sorted_readings[0],
        "recent": sorted_readings[:5],
    }


# -------------------------------------------------------------------
# 3. Save AI Consultation
# -------------------------------------------------------------------
# -------------------------------------------------------------------
# 3. Save AI Consultation (Realtime DB — strict structure)
# -------------------------------------------------------------------
@tool
def save_agent_output_tool(
    farmer_id: str,
    field_id: str,
    problems,
    solutions,
    carbon_data=None
):
    """Save AI consultation into Firebase RTDB with carbon_data included."""

    ts = datetime.utcnow().isoformat() + "Z"

    # Ensure arrays are clean
    if not isinstance(problems, list):
        problems = [str(problems)]

    if not isinstance(solutions, list):
        solutions = [str(solutions)]

    # RTDB path: Farmers/{farmer_id}/Fields/{field_id}/AIConsultations/{id}
    path = f"Farmers/{farmer_id}/Fields/{field_id}/AIConsultations"

    payload = {
        "timestamp": ts,
        "problems": problems,
        "solutions": solutions,
        "carbon_data": carbon_data or None,
    }

    # push() auto-generates a unique key
    rtdb_push(path, payload)

    return {
        "status": "saved",
        "farmer_id": farmer_id,
        "field_id": field_id,
    }
