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

---

### Step 3: Frontend Integration of NASA Horizons Ephemeris Data in `index.html`
- **Date**: 2026-11-09
- **Tool**: Antigravity (Gemini 3.8 Flash)
- **Prompt Summary**: Connect `index.html` to load `data/index.json` and the 4 real site ephemeris files via `fetch()`. Compute 10-day windows across 24 real calendar dates, use real Sun/Earth azimuth and elevation in Sky View, provide clear "NASA/JPL Horizons data" vs "Demo model" toggles and badges, add "Data & Method" section, and exclude the placeholder Science score from real decision scores.
- **Output / Deliverables**:
  - Implemented asynchronous startup (`initData()`) loading real Horizons JSON with visible progress and graceful CORS/file:// error guidance.
  - Added dual dataset switcher: "NASA/JPL Horizons (4 Real Sites)" vs "Demo Model (8 Illustrative Sites)" with distinct UI data labels.
  - Built matrix engine slicing real 240-hour windows across real calendar dates (2026-12-01 to 2027-12-31).
  - Updated Sky View to draw real Sun/Earth coordinates with 0° reference sphere horizon and disabled "Terrain mask: coming (LOLA)" placeholder toggle.
  - Excluded placeholder Science score from Decision scoring for real sites.
  - Added comprehensive "Data & Method" section documenting sources, assumptions, and coordinate references.

---

### Step 4: Topographic Horizon Mask from NASA LRO LOLA DEM
- **Date**: 2026-11-09
- **Tool**: Antigravity (Gemini 3.8 Flash)
- **Prompt Summary**: Create `data_pipeline/build_horizon_profile.py` using `rasterio`, `numpy`, and `pyproj` to process the official LRO LOLA 80 m south polar DEM (`LDEM_80S_80MPP_ADJ.TIF`). Ray-march 360° outward to 30 km at 1° steps accounting for lunar curvature drop ($\Delta z = d^2 / (2R)$) to compute maximum horizon elevation angles. Integrate the generated `data/horizon_<site>.json` into `index.html` with an interactive toggle, interpolate visibility, render the horizon profile in Sky View, and update all project documentation.
- **Output / Deliverables**:
  - Authored `data_pipeline/build_horizon_profile.py`, verifying DEM dimensions (7600x7600), resolution (80 m/px), polar stereographic projection, and 1737.4 km radius.
  - Computed 360° horizon profiles: `data/horizon_connecting_ridge.json`, `data/horizon_peak_near_shackleton.json`, `data/horizon_malapert_massif.json`, and `data/horizon_haworth.json`.
  - Updated `index.html` with linear azimuth interpolation (`getHorizonElev`), real-time terrain mask toggle (ON by default), sensitivity analysis integration, and dynamic SVG horizon silhouette.
  - Updated `docs/DATA_SOURCES.md`, `README.md`, and `AI_USAGE.md`.

---

### Step 5: Visual Redesign & 3D Interactive Lunar South Pole Globe
- **Date**: 2026-11-11
- **Tool**: Antigravity ([MODEL_NAME_TODO: user to specify])
- **Prompt Summary**: Redesign UI with dark space aesthetic and open layout. Add an interactive 3D Moon globe using Three.js with NASA LROC texture (`lroc_color_2k.jpg`), rendering Artemis III candidate landing site pins dynamically mapped to lunar surface coordinates, synced with mission parameter sliders and date selectors. Add fullscreen view, remove invented telemetry, add asset credits, and switch to local vendor scripts.
- **Output / Deliverables**:
  - Integrated Three.js 3D Moon sphere with NASA LROC 2K equirectangular texture (`lroc_color_2k.jpg`) and dynamic landing site pins.
  - Linked 3D site coordinates directly to official `REAL_SITES` lat/lon from NASA Horizons ephemerides.
  - Synced 3D pin pass/fail colors (green/red) and interactive raycaster inspection to mission requirements and selected dates.
  - Added seamless space background blending and full-view overlay with starfield.
  - Replaced hero badge telemetry with honest attribution linking to credits.
  - Added comprehensive Credits & Licences inventory table for all visual assets in `data-method`.
  - Configured local vendor paths (`vendor/three.min.js`, `vendor/OrbitControls.js`).
  - Added `*.bak` to `.gitignore`.




