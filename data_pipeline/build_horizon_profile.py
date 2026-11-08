"""
data_pipeline/build_horizon_profile.py
Build local topographic horizon elevation profiles (0-359 deg azimuth)
for lunar south pole landing sites using LRO LOLA 80m DEM (LDEM_80S_80MPP_ADJ.TIF).

NASA Space Apps Challenge 2026 - Horizon Atlas
"""
import json
import math
import os
import sys
import numpy as np
import pyproj
import rasterio

# Configuration
DEM_PATH = os.path.join("data", "raw", "LDEM_80S_80MPP_ADJ.TIF")
OUTPUT_DIR = "data"
MAX_DISTANCE_M = 30000.0  # 30 km ray-marching radius
STEP_DISTANCE_M = 80.0    # 80 m step size (matches DEM pixel resolution)
OBSERVER_HEIGHT_M = 0.0   # Default ground-level observer (0 meters above terrain)
LUNAR_RADIUS_M = 1737400.0 # 1737.4 km reference sphere radius

# 4 Official NASA Artemis III Candidate Regions (coordinates from fetch_horizons.py)
SITES = {
    "connecting_ridge": {
        "name": "Connecting Ridge (Site 01)",
        "lat": -89.46,
        "lon": 222.51,
        "source_ref": "NASA PGDA Product 78 (Barker et al. 2021 Site 01)",
    },
    "peak_near_shackleton": {
        "name": "Peak Near Shackleton (Site 07)",
        "lat": -88.81,
        "lon": 123.69,
        "source_ref": "NASA PGDA Product 78 (Barker et al. 2021 Site 07)",
    },
    "malapert_massif": {
        "name": "Malapert Massif",
        "lat": -85.99,
        "lon": 357.07,
        "source_ref": "NASA Artemis III Candidate Regions (NASA GSFC / USGS)",
    },
    "haworth": {
        "name": "Haworth",
        "lat": -87.45,
        "lon": 354.83,
        "source_ref": "NASA Artemis III Candidate Regions / IAU Gazetteer",
    },
}


def inspect_dem(src):
    print("=" * 60)
    print("LRO LOLA DEM METADATA VERIFICATION")
    print(f"File: {DEM_PATH}")
    print(f"Driver: {src.driver}")
    print(f"Dimensions: {src.width} x {src.height} pixels")
    print(f"Pixel Size (Resolution): {abs(src.transform.a):.1f} m x {abs(src.transform.e):.1f} m")
    print(f"Coordinate Reference System (CRS): {src.crs.to_string()}")
    print(f"Reference Spheroid Radius: {LUNAR_RADIUS_M / 1000.0} km")
    print(f"Nodata Value: {src.nodata}")
    print(f"Scale: {src.scales[0]}, Offset: {src.offsets[0]}")
    print(f"Coverage Bounds: {src.bounds}")
    print("Heights: Metres relative to a 1737.4 km reference sphere")
    print("=" * 60)


def compute_horizon_profile(data, transform, transformer, site_key, site_info):
    lat0_deg = site_info["lat"]
    lon0_deg = site_info["lon"]
    lat0_rad = math.radians(lat0_deg)
    lon0_rad = math.radians(lon0_deg)

    # 1. Project site lat/lon to DEM polar stereographic (x, y)
    sx, sy = transformer.transform(lon0_deg, lat0_deg)
    inv_t = ~transform
    scol, srow = [int(round(v)) for v in inv_t * (sx, sy)]

    height, width = data.shape
    if not (0 <= srow < height and 0 <= scol < width):
        raise ValueError(f"Site {site_info['name']} is outside DEM raster extent! (row={srow}, col={scol})")

    site_ground_h = float(data[srow, scol])
    if np.isnan(site_ground_h):
        print(f"Warning: Nodata encountered at site {site_info['name']} ground position!")
        site_ground_h = 0.0

    obs_total_h = site_ground_h + OBSERVER_HEIGHT_M

    print(f"\nProcessing {site_info['name']} ({site_key}):")
    print(f"  Lat/Lon: {lat0_deg:.2f}°S, {lon0_deg:.2f}°E")
    print(f"  DEM (x, y): ({sx:.1f} m, {sy:.1f} m) -> Raster (row={srow}, col={scol})")
    print(f"  Site Ground Elevation: {site_ground_h:.1f} m | Observer Height: {OBSERVER_HEIGHT_M:.1f} m")

    # Distances to sample along each ray
    dists = np.arange(STEP_DISTANCE_M, MAX_DISTANCE_M + STEP_DISTANCE_M, STEP_DISTANCE_M)
    sigmas = dists / LUNAR_RADIUS_M
    curv_drops = (dists ** 2) / (2.0 * LUNAR_RADIUS_M)

    azimuths = list(range(360))
    horizon_elevations = []

    # 2. March outward for each azimuth 0..359 degrees
    for az_deg in azimuths:
        az_rad = math.radians(az_deg)

        # Spherical forward geodesic equations
        sin_lat = np.sin(lat0_rad) * np.cos(sigmas) + np.cos(lat0_rad) * np.sin(sigmas) * np.cos(az_rad)
        lats_rad = np.arcsin(np.clip(sin_lat, -1.0, 1.0))
        y_term = np.sin(az_rad) * np.sin(sigmas) * np.cos(lat0_rad)
        x_term = np.cos(sigmas) - np.sin(lat0_rad) * sin_lat
        lons_rad = lon0_rad + np.arctan2(y_term, x_term)

        lats_deg = np.degrees(lats_rad)
        lons_deg = np.degrees(lons_rad)

        # Project sample points to polar stereographic
        xs, ys = transformer.transform(lons_deg, lats_deg)

        # Convert to pixel row/col
        cols = np.round((xs - transform.c) / transform.a).astype(int)
        rows = np.round((ys - transform.f) / transform.e).astype(int)

        # Filter valid indices within DEM bounds
        valid_mask = (rows >= 0) & (rows < height) & (cols >= 0) & (cols < width)
        if not np.any(valid_mask):
            horizon_elevations.append(0.0)
            continue

        v_rows = rows[valid_mask]
        v_cols = cols[valid_mask]
        v_dists = dists[valid_mask]
        v_curv = curv_drops[valid_mask]

        terrain_h = data[v_rows, v_cols]

        # Ignore nodata / NaN samples
        non_nan = ~np.isnan(terrain_h)
        if not np.any(non_nan):
            horizon_elevations.append(0.0)
            continue

        valid_h = terrain_h[non_nan]
        valid_d = v_dists[non_nan]
        valid_curv = v_curv[non_nan]

        # Elevation angle relative to local horizontal tangent at observer:
        # delta_z = (h_terrain - h_observer) - d^2 / (2R)
        dz = (valid_h - obs_total_h) - valid_curv
        angles_deg = np.degrees(np.arctan2(dz, valid_d))

        max_angle = float(np.max(angles_deg))
        # Horizon is at least 0 degrees (cannot see through smooth sphere)
        horizon_elevations.append(round(max(0.0, max_angle), 3))

    stats = {
        "min_deg": round(float(np.min(horizon_elevations)), 2),
        "mean_deg": round(float(np.mean(horizon_elevations)), 2),
        "max_deg": round(float(np.max(horizon_elevations)), 2),
    }

    print(f"  Horizon Profile Computed: Min={stats['min_deg']}°, Mean={stats['mean_deg']}°, Max={stats['max_deg']}°")
    if stats["max_deg"] == 0.0:
        print("  WARNING: All horizon elevation angles are 0.0°!")

    return {
        "site_id": site_key,
        "site_name": site_info["name"],
        "lat": lat0_deg,
        "lon": lon0_deg,
        "ground_height_m": round(site_ground_h, 1),
        "observer_height_m": OBSERVER_HEIGHT_M,
        "dem_file": os.path.basename(DEM_PATH),
        "dem_resolution_m": STEP_DISTANCE_M,
        "max_distance_km": MAX_DISTANCE_M / 1000.0,
        "lunar_radius_km": LUNAR_RADIUS_M / 1000.0,
        "stats": stats,
        "azimuths": azimuths,
        "horizon_elevations_deg": horizon_elevations,
    }


def main():
    if not os.path.exists(DEM_PATH):
        print(f"ERROR: DEM file not found at {DEM_PATH}!")
        print("Please ensure LDEM_80S_80MPP_ADJ.TIF is placed in data/raw/")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Opening LRO LOLA DEM...")
    with rasterio.open(DEM_PATH) as src:
        inspect_dem(src)
        print("Loading elevation raster into memory (7600 x 7600 float32, ~231 MB)...")
        data = src.read(1)
        transform = src.transform

    # Coordinate transformation
    proj_moon = pyproj.CRS("+proj=stere +lat_0=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R=1737400 +units=m +no_defs")
    proj_latlon = pyproj.CRS("+proj=longlat +R=1737400 +no_defs")
    transformer = pyproj.Transformer.from_crs(proj_latlon, proj_moon, always_xy=True)

    summary_results = {}
    for key, site in SITES.items():
        profile = compute_horizon_profile(data, transform, transformer, key, site)
        out_path = os.path.join(OUTPUT_DIR, f"horizon_{key}.json")
        with open(out_path, "w") as f:
            json.dump(profile, f, indent=2)
        print(f"  -> Saved {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")
        summary_results[key] = profile["stats"]

    print("\n" + "=" * 60)
    print("HORIZON PROFILING COMPLETE SUMMARY:")
    for k, v in summary_results.items():
        print(f"  {SITES[k]['name']:<30}: Min={v['min_deg']:>5.2f}°, Mean={v['mean_deg']:>5.2f}°, Max={v['max_deg']:>5.2f}°")
    print("=" * 60)


if __name__ == "__main__":
    main()

