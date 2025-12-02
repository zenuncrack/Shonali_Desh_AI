import ee
from datetime import datetime
from langchain_core.tools import tool

# Initialize GEE (safe for repeated imports)
try:
    ee.Initialize(project='manifest-actor-479417-c6')
except Exception:
    ee.Authenticate()
    ee.Initialize(project='manifest-actor-479417-c6')

# ---- Index formulas ----
def compute_ndssi(image):
    salt = image.normalizedDifference(["B11", "B12"])  # NDSSI
    return image.addBands(salt.rename("NDSSI"))

def compute_ndre(image):
    ndre = image.normalizedDifference(["B8", "B5"])  # Nitrogen proxy
    return image.addBands(ndre.rename("NDRE"))

def compute_ndni(image):
    ndni = image.normalizedDifference(["B3", "B4"])  # Extra N index
    return image.addBands(ndni.rename("NDNI"))


@tool
def fetch_satellite_tool(lat: float, lon: float):
    """
    Fetch NDSSI, NDRE, NDNI from Sentinel-2 surface reflectance.
    """

    point = ee.Geometry.Point(lon, lat)

    # Sentinel-2 surface reflectance (best suited for agronomy)
    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR")
        .filterBounds(point)
        .filterDate("2024-01-01", datetime.utcnow().strftime("%Y-%m-%d"))
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
    )

    image = ee.Image(collection.sort("system:time_start", False).first())

    if image is None:
        return {"error": "No satellite data found for this location"}

    # Add indexes
    image = compute_ndssi(image)
    image = compute_ndre(image)
    image = compute_ndni(image)

    # Sample pixel
    pixel = image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=10,
        bestEffort=True
    ).getInfo()

    return {
        "lat": lat,
        "lon": lon,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "NDSSI": float(pixel.get("NDSSI", None)),
        "NDRE": float(pixel.get("NDRE", None)),
        "NDNI": float(pixel.get("NDNI", None)),
    }
