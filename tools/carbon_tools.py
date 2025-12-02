# tools/carbon_tools.py

import ee
from datetime import datetime
from langchain_core.tools import tool
from config.settings import DEMO_MODE

# -----------------------------
# Initialize Earth Engine safely
# -----------------------------
try:
    ee.Initialize(project="manifest-actor-479417-c6")
except Exception:
    try:
        ee.Authenticate()
        ee.Initialize(project="manifest-actor-479417-c6")
    except:
        print("⚠️ Earth Engine authentication failed.")


# -----------------------------
# Helper: Compute NDVI at point
# -----------------------------
def _compute_ndvi(lat: float, lon: float):
    try:
        point = ee.Geometry.Point([lon, lat])

        img = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(point)
            .filterDate("2024-01-01", datetime.utcnow().strftime("%Y-%m-%d"))
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
            .select(["B8", "B4"])
            .median()
        )

        ndvi = img.normalizedDifference(["B8", "B4"]).rename("NDVI")

        return ndvi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=10,
        ).get("NDVI")
    except Exception as e:
        print("⚠️ NDVI computation error:", e)
        return None


# -----------------------------
# Method 1 — Viewport Carbon Method
# -----------------------------
def _carbon_from_viewport(ndvi_value: float, area_ha: float = 1.0):
    if ndvi_value is None:
        return None

    carbon_per_ha = float(ndvi_value) * 2
    total_carbon = carbon_per_ha * area_ha
    revenue = total_carbon * 15

    return {
        "area_ha": area_ha,
        "carbonPerHa": carbon_per_ha,
        "totalCarbon": total_carbon,
        "revenue": revenue,
    }


# -----------------------------
# Method 2 — Point Rating Method
# -----------------------------
def _carbon_from_point(ndvi_value: float):
    if ndvi_value is None:
        return None

    ndvi_value = float(ndvi_value)

    if ndvi_value > 0.4:
        rating = "High"
        potential = 1.5
    elif ndvi_value >= 0.2:
        rating = "Moderate"
        potential = 0.8
    else:
        rating = "Low"
        potential = 0.2

    revenue = potential * 15

    return {
        "rating": rating,
        "potentialPerHa": potential,
        "revenue": revenue,
    }


# -----------------------------
# LangChain Tool — used by LangGraph
# -----------------------------
@tool
def fetch_carbon_from_ndvi(lat: float, lon: float, area_ha: float = 1.0):
    """
    Compute NDVI → Carbon Sequestration using simplified models.
    Safe for LangGraph + RTDB architecture.
    """

    # DEMO MODE shortcut
    if DEMO_MODE:
        return {
            "lat": lat,
            "lon": lon,
            "ndvi": 0.35,
            "viewport_method": _carbon_from_viewport(0.35),
            "point_method": _carbon_from_point(0.35),
            "note": "DEMO_MODE enabled",
        }

    ndvi_number = _compute_ndvi(lat, lon)

    try:
        ndvi_value = ee.Number(ndvi_number).getInfo()
    except:
        ndvi_value = None

    viewport = _carbon_from_viewport(ndvi_value, area_ha)
    point = _carbon_from_point(ndvi_value)

    return {
        "lat": lat,
        "lon": lon,
        "ndvi": ndvi_value,
        "viewport_method": viewport,
        "point_method": point,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
