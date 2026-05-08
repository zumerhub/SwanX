import rasterio
import numpy as np
import geopandas as gpd
from rasterio.features import shapes

green = rasterio.open("B03.jp2").read(1).astype(float)
nir = rasterio.open("B08.jp2").read(1).astype(float)

ndwi = (green - nir) / (green + nir + 1e-6)

# Flood mask
flood = ndwi > 0.3

# Convert to polygons
results = (
    {'properties': {'value': v}, 'geometry': s}
    for i, (s, v) in enumerate(
        shapes(flood.astype(np.uint8), mask=flood)
    )
)

gdf = gpd.GeoDataFrame.from_features(list(results))
gdf.to_file("flood_polygons.geojson")