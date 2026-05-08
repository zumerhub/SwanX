# save as: download_lagos_s2.py
# pip install pystac-client requests

from pystac_client import Client
import requests, os, pathlib

# ── Lagos bounding box ───────────────────────────────
BBOX = [3.0, 6.2, 3.8, 6.8]   # lon_min, lat_min, lon_max, lat_max

SEARCHES = {
    "pre_event":  ("2023-01-01", "2023-02-28"),   # dry season
    "post_event": ("2023-07-01", "2023-08-31"),    # rainy/flood season
}

BANDS = ["green", "nir", "swir16"]   # B03, B08, B11 asset keys in Earth Search v1

api = Client.open("https://earth-search.aws.element84.com/v1")

for folder, (start, end) in SEARCHES.items():
    out_dir = pathlib.Path(f"data/sentinel2/{folder}")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n── Searching {folder} ({start} → {end}) ──")
    results = api.search(
        collections=["sentinel-2-l2a"],
        bbox=BBOX,
        datetime=f"{start}/{end}",
        query={"eo:cloud_cover": {"lt": 20}},
        max_items=3,
        sortby="+properties.eo:cloud_cover",   # clearest first
    )

    items = list(results.items())
    if not items:
        print("  No scenes found — try relaxing cloud cover to 30")
        continue

    # Pick the cleanest scene
    best = items[0]
    print(f"  Scene  : {best.id}")
    print(f"  Date   : {best.datetime}")
    print(f"  Cloud  : {best.properties['eo:cloud_cover']}%")

    for band_key in BANDS:
        if band_key not in best.assets:
            print(f"  WARN: {band_key} not in assets, skipping")
            continue

        href = best.assets[band_key].href
        filename = out_dir / f"{band_key}.tif"
        print(f"  Downloading {band_key} → {filename}")
        print(f"    URL: {href}")

        r = requests.get(href, stream=True, timeout=60)
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
        print(f"    ✓ {filename.stat().st_size / 1024 / 1024:.1f} MB")

print("\nDone. Check data/sentinel2/")