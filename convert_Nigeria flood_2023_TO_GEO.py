import geopandas as gpd

dir = r"C:\samcodebase\SwanX\data\nigeri_flood_2023"

file = "2022_Flood-affected_Areas_2022_by_LGA_as_of_8th_August.shp"

gdf = gpd.read_file(f"{dir}\\{file}")

print(gdf.head())
print(gdf.crs)

gdf.to_file(f"{dir}\\nigeria_flood.geojson", driver="GeoJSON")