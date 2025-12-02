# tools/flood_tools.py

import os
import calendar
from datetime import date, datetime
from typing import Dict, Any, List, Optional

import requests
from langchain_core.tools import tool
from config.settings import FLOOD_MODEL_PATH, DEMO_MODE

# --------------------------------------------------
# Load PKL model ONLY when DEMO_MODE is FALSE
# --------------------------------------------------
flood_model = None
if not DEMO_MODE:
    import joblib

    if os.path.exists(FLOOD_MODEL_PATH):
        try:
            flood_model = joblib.load(FLOOD_MODEL_PATH)
            print("[flood_tools] Flood model loaded successfully.")
        except Exception as e:
            print(f"[flood_tools] ERROR loading flood model: {e}")
            flood_model = None
    else:
        print(f"[flood_tools] Warning: flood model not found at {FLOOD_MODEL_PATH}")
else:
    print("[flood_tools] DEMO_MODE=True: flood model will not be loaded.")


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def _month_date_range(year: int, month: int):
    start = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end = date(year, month, last_day)
    return start, end


def _last_n_full_months(n: int = 3):
    today = date.today()
    year = today.year
    month = today.month

    months = []
    for _ in range(n):
        month -= 1
        if month == 0:
            month = 12
            year -= 1
        months.append((year, month))

    months.reverse()
    return months


def _fetch_monthly_avg_temp(lat: float, lon: float, year: int, month: int):
    start, end = _month_date_range(year, month)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": "temperature_2m_mean",
        "timezone": "UTC",
    }

    resp = requests.get(url, params=params, timeout=30)
    if resp.status_code != 200:
        print(f"[flood_tools] Open-Meteo error {resp.status_code}: {resp.text}")
        return None

    data = resp.json()
    temps = data.get("daily", {}).get("temperature_2m_mean", [])

    if not temps:
        print(f"[flood_tools] No temps for {year}-{month:02d}")
        return None

    clean = [t for t in temps if t is not None]
    if not clean:
        return None

    return sum(clean) / len(clean)


def _categorize_flood_risk(pred: float) -> str:
    if pred < 100:
        return "low"
    elif pred < 250:
        return "medium"
    return "high"


# --------------------------------------------------
# LangChain Tool
# --------------------------------------------------
@tool
def fetch_flood_risk_tool(lat: float, lon: float) -> Dict[str, Any]:
    """
    Predict monthly rainfall and flood risk using the flood_model.pkl.
    Computes last 3 full months' average temperatures automatically.
    """

    # DEMO MODE
    if DEMO_MODE:
        return {
            "mode": "demo",
            "lat": lat,
            "lon": lon,
            "features": {
                "month_1_avg_temp": 27.5,
                "month_2_avg_temp": 28.1,
                "month_3_avg_temp": 29.0,
                "current_month": datetime.utcnow().month,
            },
            "predicted_rainfall_mm": 320.0,
            "flood_risk": "high",
        }

    # REAL MODE
    months = _last_n_full_months(3)
    temps = []

    for y, m in months:
        avg = _fetch_monthly_avg_temp(lat, lon, y, m)
        temps.append(avg)

    if any(t is None for t in temps):
        return {
            "mode": "real",
            "error": "Could not retrieve temperature data.",
            "months": [
                {"year": y, "month": m, "avg_temp": t}
                for (y, m), t in zip(months, temps)
            ],
        }

    m1, m2, m3 = temps
    current_month = datetime.utcnow().month

    features = [m1, m2, m3, current_month]

    if flood_model is None:
        return {
            "mode": "real",
            "warning": "Flood model not loaded.",
            "features": {
                "month_1_avg_temp": m1,
                "month_2_avg_temp": m2,
                "month_3_avg_temp": m3,
                "current_month": current_month,
            },
        }

    try:
        predicted = float(flood_model.predict([features])[0])
    except Exception as e:
        return {
            "mode": "real",
            "error": f"Model prediction failed: {e}",
            "features": features,
        }

    risk = _categorize_flood_risk(predicted)

    return {
        "mode": "real",
        "lat": lat,
        "lon": lon,
        "months": [
            {"year": y, "month": m, "avg_temp": t}
            for (y, m), t in zip(months, temps)
        ],
        "features": {
            "month_1_avg_temp": m1,
            "month_2_avg_temp": m2,
            "month_3_avg_temp": m3,
            "current_month": current_month,
        },
        "predicted_rainfall_mm": predicted,
        "flood_risk": risk,
    }
