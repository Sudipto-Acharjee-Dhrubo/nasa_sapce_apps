"""
fetch_horizons.py
Fetch hourly Sun and Earth azimuth/elevation as seen from points on the Moon
using NASA/JPL Horizons API (https://ssd.jpl.nasa.gov/api/horizons.api).

Supports long time-ranges via 90-day chunking and saves compact column-array JSON.
"""
from datetime import datetime, timedelta
import json
import os
import time
import requests

API = "https://ssd.jpl.nasa.gov/api/horizons.api"

# 4 Official NASA Artemis III Candidate Regions / High Priority Sites
# Sources documented in docs/DATA_SOURCES.md
SITES = {
    "connecting_ridge": {
        "name": "Connecting Ridge (Site 01)",
        "lat": -89.46,
        "lon": 222.51,  # 137.49 W
        "alt_km": 0.0,
        "source_ref": "NASA PGDA Product 78 (Barker et al. 2021 Site 01)",
    },
    "peak_near_shackleton": {
        "name": "Peak Near Shackleton (Site 07)",
        "lat": -88.81,
        "lon": 123.69,
        "alt_km": 0.0,
        "source_ref": "NASA PGDA Product 78 (Barker et al. 2021 Site 07)",
    },
    "malapert_massif": {
        "name": "Malapert Massif",
        "lat": -85.99,
        "lon": 357.07,  # 2.93 W
        "alt_km": 0.0,
        "source_ref": "NASA Artemis III Candidate Regions (NASA GSFC / USGS)",
    },
    "haworth": {
        "name": "Haworth",
        "lat": -87.45,
        "lon": 354.83,  # 5.17 W
        "alt_km": 0.0,
        "source_ref": "NASA Artemis III Candidate Regions / IAU Gazetteer",
    },
}

START = "2026-12-01 00:00"
STOP = "2027-12-31 00:00"
STEP = "1 h"
CHUNK_DAYS = 90
MASK_DEG = 0.0  # Geometric reference sphere horizon


def generate_chunks(start_str, stop_str, chunk_days=CHUNK_DAYS):
    start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
    stop_dt = datetime.strptime(stop_str, "%Y-%m-%d %H:%M")
    cur = start_dt
    chunks = []
    while cur < stop_dt:
        nxt = min(cur + timedelta(days=chunk_days), stop_dt)
        chunks.append((cur.strftime("%Y-%m-%d %H:%M"), nxt.strftime("%Y-%m-%d %H:%M")))
        cur = nxt
    return chunks


def fetch_body_chunk(body_id, site, chunk_start, chunk_stop):
    """body_id: '10' = Sun, '399' = Earth. Returns dict of time -> (az, el)."""
    params = {
        "format": "json",
        "COMMAND": f"'{body_id}'",
        "OBJ_DATA": "'NO'",
        "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": "'OBSERVER'",
        "CENTER": "'coord@301'",          # 301 = Moon
        "COORD_TYPE": "'GEODETIC'",
        "SITE_COORD": f"'{site['lon']},{site['lat']},{site['alt_km']}'",
        "START_TIME": f"'{chunk_start}'",
        "STOP_TIME": f"'{chunk_stop}'",
        "STEP_SIZE": f"'{STEP}'",
        "QUANTITIES": "'4'",              # 4 = apparent azimuth & elevation
        "ANG_FORMAT": "'DEG'",
        "CSV_FORMAT": "'YES'",
    }
    
    # Retry logic for robustness
    for attempt in range(3):
        try:
            r = requests.get(API, params=params, timeout=60)
            r.raise_for_status()
            break
        except Exception as err:
            if attempt == 2:
                raise
            time.sleep(2)

    text = r.json().get("result", "")
    if "$$SOE" not in text:
        raise RuntimeError("Horizons returned no data block:\n" + text[:800])
    block = text.split("$$SOE")[1].split("$$EOE")[0].strip().splitlines()
    data = {}
    for line in block:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 4:
            continue
        # CSV columns: date, (flags), (flags), azimuth, elevation, ...
        nums = []
        for p in parts[1:]:
            try:
                nums.append(float(p))
            except ValueError:
                pass
        if len(nums) >= 2:
            az, el = nums[0], nums[1]
            data[parts[0]] = (az, el)
    return data


def fetch_body(body_id, site):
    chunks = generate_chunks(START, STOP)
    merged = {}
    for c_start, c_stop in chunks:
        chunk_data = fetch_body_chunk(body_id, site, c_start, c_stop)
        merged.update(chunk_data)
        time.sleep(0.2)  # courteous API pacing
    return merged


def longest_run_false(flags):
    best = cur = 0
    for f in flags:
        cur = 0 if f else cur + 1
        best = max(best, cur)
    return best


def compute_metrics(sun_el, earth_el, mask_deg=MASK_DEG):
    hours = len(sun_el)
    if hours == 0:
        return {"sunlight_pct": 0.0, "longest_darkness_h": 0, "earth_contact_days_pct": 0.0}
    sun_vis = [el > mask_deg for el in sun_el]
    earth_vis = [el > mask_deg for el in earth_el]
    days = max(1, hours // 24)
    earth_days = sum(
        any(earth_vis[d * 24:min((d + 1) * 24, hours)]) for d in range(days)
    )
    return {
        "sunlight_pct": round(100.0 * sum(sun_vis) / hours, 1),
        "longest_darkness_h": longest_run_false(sun_vis),
        "earth_contact_days_pct": round(100.0 * earth_days / days, 1),
    }


def analyse_site(key, site):
    print(f"Fetching Sun ephemeris for {site['name']}...")
    sun_dict = fetch_body("10", site)
    print(f"Fetching Earth ephemeris for {site['name']}...")
    earth_dict = fetch_body("399", site)

    # Intersection of timestamps sorted chronologically
    common_times = sorted(set(sun_dict.keys()) & set(earth_dict.keys()))
    times = []
    sun_el = []
    sun_az = []
    earth_el = []
    earth_az = []

    for t in common_times:
        s_az, s_el = sun_dict[t]
        e_az, e_el = earth_dict[t]
        times.append(t)
        sun_az.append(round(s_az, 2))
        sun_el.append(round(s_el, 3))
        earth_az.append(round(e_az, 2))
        earth_el.append(round(e_el, 3))

    total_h = len(times)
    overall = compute_metrics(sun_el, earth_el)

    # Compute 10-day sample windows (240 hours each) across seasons
    sample_windows = []
    sample_starts = [
        "2026-Dec-01 00:00",
        "2027-Mar-15 00:00",
        "2027-Jun-15 00:00",
        "2027-Sep-15 00:00",
        "2027-Dec-01 00:00",
    ]
    for s_start in sample_starts:
        if s_start in times:
            idx = times.index(s_start)
            w_sun = sun_el[idx:idx + 240]
            w_earth = earth_el[idx:idx + 240]
            w_metrics = compute_metrics(w_sun, w_earth)
            w_metrics["start"] = s_start
            w_metrics["hours"] = len(w_sun)
            sample_windows.append(w_metrics)

    result = {
        "site_id": key,
        "name": site["name"],
        "lat": site["lat"],
        "lon": site["lon"],
        "alt_km": site["alt_km"],
        "source": "NASA/JPL Horizons (geometric, no terrain mask)",
        "source_ref": site["source_ref"],
        "mask_deg": MASK_DEG,
        "window": [START, STOP],
        "step": STEP,
        "total_hours": total_h,
        "overall_stats": overall,
        "sample_windows_10d": sample_windows,
        "times": times,
        "sun_el": sun_el,
        "sun_az": sun_az,
        "earth_el": earth_el,
        "earth_az": earth_az,
    }
    return result


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    index_sites = []
    
    print(f"Starting Horizons ephemeris fetch for {len(SITES)} sites ({START} to {STOP})...")
    for key, site in SITES.items():
        t0 = time.time()
        res = analyse_site(key, site)
        path = f"data/{key}.json"
        with open(path, "w") as f:
            json.dump(res, f)
        
        file_size_kb = os.path.getsize(path) / 1024.0
        elapsed = round(time.time() - t0, 1)
        
        print(f"\n[{key}] saved to {path} ({file_size_kb:.1f} KB in {elapsed}s)")
        print(f"  Overall: Sun {res['overall_stats']['sunlight_pct']}% | "
              f"Max dark: {res['overall_stats']['longest_darkness_h']}h | "
              f"Earth days: {res['overall_stats']['earth_contact_days_pct']}%")
        print("  Sample 10-day windows:")
        for w in res["sample_windows_10d"]:
            print(f"    - {w['start']}: Sun {w['sunlight_pct']}%, Max Dark {w['longest_darkness_h']}h, Earth {w['earth_contact_days_pct']}%")
        
        index_sites.append({
            "id": key,
            "name": site["name"],
            "lat": site["lat"],
            "lon": site["lon"],
            "alt_km": site["alt_km"],
            "file": f"{key}.json",
            "source": "NASA/JPL Horizons",
            "source_ref": site["source_ref"],
            "overall_stats": res["overall_stats"],
            "sample_windows_10d": res["sample_windows_10d"],
        })

    index_data = {
        "updated": datetime.now().isoformat(),
        "source": "NASA/JPL Horizons",
        "window": [START, STOP],
        "sites": index_sites,
    }
    with open("data/index.json", "w") as f:
        json.dump(index_data, f, indent=2)
    print("\nSuccessfully updated data/index.json!")
