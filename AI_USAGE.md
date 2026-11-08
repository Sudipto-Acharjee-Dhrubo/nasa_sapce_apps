# AI Usage Disclosure Log

In compliance with NASA Space Apps Challenge regulations, this document records all AI assistance, tools, prompts, and deliverables throughout the development of **Horizon Atlas**.

---

### Step 0: Initial Codebase & Proposal Review
- **Date**: 2026-11-08
- **Tool**: Antigravity (Gemini 3.8 Flash)
- **Prompt Summary**: Read project proposal PDF and `index.html`. Summarize the demo calculation model in 10 lines, identify functions/data to replace, and propose the minimal change plan without editing files yet.
- **Output / Deliverables**: Generated a 10-line architectural review detailing the synthetic sinusoidal approximations (`hor`, `sun`, `earth`, `M`) and presented the step-by-step migration plan to NASA open data.

---

### Step 1: Verification & Refinement of `fetch_horizons.py`
- **Date**: 2026-11-08
- **Tool**: Antigravity (Gemini 3.8 Flash)
- **Prompt Summary**: Test `fetch_horizons.py` against NASA/JPL Horizons API for a test polar site, ensure network error recovery, verify sensible polar astronomical outputs, and record azimuth values needed for terrain profiling and sky views.
- **Output / Deliverables**:
  - Configured `.gitignore` to prevent committing raw DEM GeoTIFF files and local environments.
  - Enhanced `fetch_horizons.py` to record `sun_az` and `earth_az` alongside elevations.
  - Added automated index generation (`data/index.json`).
  - Tested on test polar coordinate (lat -89.5°, lon 0.0°); verified slow polar oscillation (Sun elevation: +0.93° to +1.56°, Earth elevation: -1.11° to -6.34°).
  - Authored `docs/DATA_SOURCES.md` registering NASA JPL Horizons, LRO LOLA, and PGDA references.

---

### Step 2: Real Artemis III Candidate Sites & 13-Month Horizons Ephemeris
- **Date**: 2026-11-09
- **Tool**: Antigravity (Gemini 3.8 Flash)
- **Prompt Summary**: Derive official NASA coordinates for 4 Artemis III candidate regions (Connecting Ridge, Peak Near Shackleton, Malapert Massif, Haworth) from NASA PGDA Product 78 (Barker et al. 2021) and NASA GSFC/USGS benchmarks. Fetch hourly Sun and Earth positions across 2026-12-01 to 2027-12-31 using 90-day chunking. Store results in compact column-array JSON and report multi-window metrics.
- **Output / Deliverables**:
  - Registered all 4 site coordinates and their official NASA publications in `docs/DATA_SOURCES.md`.
  - Refactored `fetch_horizons.py` with 90-day window chunking and retry handlers to fetch 9,481 hourly points per site.
  - Implemented compact column-array schema (`times`, `sun_el`, `sun_az`, `earth_el`, `earth_az`), reducing storage by ~70% (~465 KB per site).
  - Generated `data/connecting_ridge.json`, `data/peak_near_shackleton.json`, `data/malapert_massif.json`, `data/haworth.json`, and `data/index.json`.
  - Analyzed and verified distinct astronomical variation across lunar latitudes, longitudes, and seasons.


