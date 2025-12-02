"""from tools.flood_tools import fetch_flood_risk_tool

result = fetch_flood_risk_tool.invoke({"lat": 23.5, "lon": 90.3})
print(result)"""

from tools.carbon_tools import fetch_carbon_from_ndvi

lat = 23.8103
lon = 90.4125

result = fetch_carbon_from_ndvi.invoke({
    "lat": lat,
    "lon": lon,
    "area_ha": 1.0
})

print(result)

