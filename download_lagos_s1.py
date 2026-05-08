# save as: download_lagos_s1.py
# pip install pystac-client requests

from pystac_client import Client
import requests
import pathlib
import time

# ── Lagos bounding box ───────────────────────────────
BBOX = [3.0, 6.2, 3.8, 6.8]

SEARCHES = {
    "pre_event": ("2023-01-01", "2023-02-28"),
    "post_event_1": ("2023-06-01", "2023-07-15"),
    "post_event_2": ("2023-07-15", "2023-08-31"),
}

# Sentinel-1 polarizations
POLARIZATION = ["vv", "vh"]

# STAC API
api = Client.open("https://earth-search.aws.element84.com/v1")

# Reusable session (faster + stable)
session = requests.Session()


# ── Robust downloader ───────────────────────────────
def download_file(url, filename, retries=3):
    for attempt in range(retries):
        try:
            with session.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
            return True

        except Exception as e:
            print(f"    ⚠️ Attempt {attempt+1} failed: {e}")
            time.sleep(5)

    print(f"    ❌ Failed to download: {filename}")
    return False


# ── Safe search (retry STAC API) ─────────────────────
def safe_search(**kwargs):
    for attempt in range(3):
        try:
            return api.search(**kwargs)
        except Exception as e:
            print(f"Retry {attempt+1}/3 due to error: {e}")
            time.sleep(5)
    raise Exception("STAC search failed after retries")


# ── Main loop ───────────────────────────────────────
for folder, (start, end) in SEARCHES.items():
    out_dir = pathlib.Path(f"data/sentinel1/{folder}")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n── Searching {folder} ({start} → {end}) ──")

    results = safe_search(
        collections=["sentinel-1-grd"],
        bbox=BBOX,
        datetime=f"{start}/{end}",
        query={
            "sar:instrument_mode": {"eq": "IW"},
            "sar:polarizations": {"contains": "VH"},
        },
        max_items=5,
    )

    # Limit results to avoid API overload
    items = []
    for i, item in enumerate(results.items()):
        if i >= 2:  # only take 2 scenes
            break
        items.append(item)

    if not items:
        print("  No scenes found — try expanding date or removing filters")
        continue

    best = items[0]

    print(f"  Scene  : {best.id}")
    print(f"  Date   : {best.datetime}")

    for pol in POLARIZATION:
        if pol not in best.assets:
            print(f"  WARN: {pol} not available")
            continue

        href = best.assets[pol].href

        # Convert S3 → HTTPS
        href = href.replace(
            "s3://sentinel-s1-l1c/",
            "https://sentinel-s1-l1c.s3.amazonaws.com/"
        )

        filename = out_dir / f"{pol}.tif"

        # Skip if already downloaded
        if filename.exists():
            print(f"  ⏭️ Skipping {filename} (already exists)")
            continue

        print(f"  Downloading {pol} → {filename}")
        print(f"    URL: {href}")

        success = download_file(href, filename)

        if success:
            size_mb = filename.stat().st_size / 1024 / 1024
            print(f"    ✓ {size_mb:.1f} MB")

print("\n✅ Done. Check data/sentinel1/")