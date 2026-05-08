import geopandas as gpd

path = r"C:\samcodebase\SwanX\data\nigeri_flood_2023\nigeria_flood.geojson"

gdf = gpd.read_file(path)

print(gdf.head())
print("\nColumns:", gdf.columns)
print("\nCRS:", gdf.crs)
print("\nGeometry type:", gdf.geom_type.unique())