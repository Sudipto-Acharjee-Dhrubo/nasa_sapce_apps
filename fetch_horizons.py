"""
fetch_horizons.py
Fetch hourly Sun and Earth azimuth/elevation as seen from a point on the Moon
using NASA/JPL Horizons, then compute simple visibility numbers.

Run:   python fetch_horizons.py
Needs: pip install requests
Output: data/<site>.json

NOTE: Elevation here is measured from a smooth Moon (no terrain).
Terrain (LRO LOLA horizon mask) comes later; MASK_DEG is a placeholder for it.
"""
import json
import os
import requests

API = "https://ssd.jpl.nasa.gov/api/horizons.api"

# ---- EDIT THESE ----------------------------------------------------------
# Replace with real site coordinates from your demo / the challenge site list.
# lon in degrees EAST (0-360 ok), lat in degrees, alt in km above reference sphere.
SITES = {
    "site_example": {"lon": 0.0, "lat": -89.5, "alt_km": 0.0},
}
START = "2026-12-01 00:00"
STOP = "2026-12-11 00:00"   # 10-day window like your demo
STEP = "1 h"
MASK_DEG = 0.0              # minimum elevation to count as "visible"
# --------------------------------------------------------------------------


def fetch_body(body_id, site):
    """body_id: '10' = Sun, '399' = Earth. Returns list of (time, az, el)."""
    params = {
        "format": "json",
        "COMMAND": f"'{body_id}'",
        "OBJ_DATA": "'NO'",
        "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": "'OBSERVER'",
        "CENTER": "'coord@301'",          # 301 = Moon
        "COORD_TYPE": "'GEODETIC'",
        "SITE_COORD": f"'{site['lon']},{site['lat']},{site['alt_km']}'",
        "START_TIME": f"'{START}'",
        "STOP_TIME": f"'{STOP}'",
        "STEP_SIZE": f"'{STEP}'",
        "QUANTITIES": "'4'",              # 4 = apparent azimuth & elevation
        "ANG_FORMAT": "'DEG'",
        "CSV_FORMAT": "'YES'",
    }
    r = requests.get(API, params=params, timeout=60)
    r.raise_for_status()
    text = r.json()["result"]
    if "$$SOE" not in text:
        raise RuntimeError("Horizons returned no data:\n" + text[:800])
    block = text.split("$$SOE")[1].split("$$EOE")[0].strip().splitlines()
    rows = []
    for line in block:
        parts = [p.strip() for p in line.split(",")]
        # CSV columns: date, (flags), (flags), azimuth, elevation, ...
        nums = []
        for p in parts[1:]:
            try:
                nums.append(float(p))
            except ValueError:
                pass
        az, el = nums[0], nums[1]
        rows.append((parts[0], az, el))
    return rows


def longest_run_false(flags):
    best = cur = 0
    for f in flags:
        cur = 0 if f else cur + 1
        best = max(best, cur)
    return best


def analyse(name, site):
    sun = fetch_body("10", site)
    earth = fetch_body("399", site)
    sun_vis = [el > MASK_DEG for _, _, el in sun]
    earth_vis = [el > MASK_DEG for _, _, el in earth]

    hours = len(sun)
    days = max(1, hours // 24)
    earth_days = sum(
        any(earth_vis[d * 24:(d + 1) * 24]) for d in range(days)
    )
    result = {
        "site": name,
        "source": "NASA/JPL Horizons (geometric, no terrain mask)",
        "mask_deg": MASK_DEG,
        "window": [START, STOP],
        "sunlight_pct": round(100 * sum(sun_vis) / hours, 1),
        "longest_darkness_h": longest_run_false(sun_vis),
        "earth_contact_days_pct": round(100 * earth_days / days, 1),
        "hourly": [
            {
                "t": s[0],
                "sun_az": round(s[1], 2),
                "sun_el": round(s[2], 3),
                "earth_az": round(e[1], 2),
                "earth_el": round(e[2], 3),
            }
            for s, e in zip(sun, earth)
        ],
    }
    return result


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    index_sites = []
    for name, site in SITES.items():
        out = analyse(name, site)
        path = f"data/{name}.json"
        with open(path, "w") as f:
            json.dump(out, f, indent=2)
        print(name, "->", path,
              "| sun %:", out["sunlight_pct"],
              "| longest dark (h):", out["longest_darkness_h"],
              "| earth days %:", out["earth_contact_days_pct"])
        index_sites.append({
            "id": name,
            "name": name.replace("_", " ").title(),
            "lat": site["lat"],
            "lon": site["lon"],
            "alt_km": site["alt_km"],
            "file": f"{name}.json",
            "source": "NASA/JPL Horizons"
        })
    with open("data/index.json", "w") as f:
        json.dump({"sites": index_sites, "window": [START, STOP]}, f, indent=2)
    print("Generated data/index.json")
