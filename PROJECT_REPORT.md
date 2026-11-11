# Horizon Atlas · Project Architecture & Comprehensive Report
**Lunar Landing Site Navigator · NASA Space Apps Challenge 2026**  
**Team VOIDBRONE**

---

## 1. Executive Summary: What is Horizon Atlas?

### 1.1 The Challenge
Landing a robotic or crewed lander on the Moon’s South Pole (e.g. for NASA’s **Artemis III** or CLPS missions) is an extreme engineering challenge. Because the Sun hugs the lunar horizon at grazing angles (rarely rising more than 1.5°–3.0° above flat ground), colossal craters and elevated massifs cast elongated, dynamic shadows that can plunge a landing site into darkness for weeks. Simultaneously, the Earth wobbles low along the horizon due to lunar libration, intermittently severing direct line-of-sight communications.

Most existing mission analysis software tools operate in a **forward-only** manner: a mission planner picks a specific crater or ridge, runs orbital mechanics models, and inspects what happens at that single spot.

### 1.2 Our Solution: The Inverse Problem
**Horizon Atlas flips this paradigm around:**
> **You specify what your lander needs to survive, and Horizon Atlas instantly tells you WHERE and WHEN you can land.**

The user specifies three mission requirements:
1. **Minimum sunlight percentage** required for solar power generation (e.g. at least 55%).
2. **Maximum continuous darkness hours** the onboard batteries can survive (e.g. under 90 hours).
3. **Minimum Earth contact days** required for direct-to-Earth communication (e.g. at least 70% of mission days).

Horizon Atlas scans all evaluated candidate regions across a full **13-month operational window (9,481 hourly ephemeris steps)**, models terrain blockage in 360° from real elevation maps, ranks every possible 10-day mission opportunity, simulates battery dynamics, and provides **explainable decision breakdowns** without black-box machine learning.

---

## 2. Core Scientific Pillars & Open Science Principles

In accordance with NASA Open Science guidelines and NASA Space Apps Challenge rules, Horizon Atlas strictly adheres to three design philosophies:
1. **Zero Invented Telemetry & Coordinates**: Every geographic coordinate, horizon elevation angle, and astronomical azimuth/elevation is computed from verified NASA datasets.
2. **Deterministic Physics over Black-Box AI**: Every recommendation is computed from orbital geometry, ray-marched terrain shadows, and energy conservation. The tool explains exactly why a site wins or fails, and by how many percentage points or hours.
3. **Honest Scientific Limitations**: Differences between our ground-level mission simulations and published orbital multi-year averages (e.g. NASA LOLA benchmarks) are explicitly disclosed and explained.

---

## 3. Evaluated Artemis III Candidate Landing Sites

Horizon Atlas models four official Artemis III candidate regions using official NASA coordinates and elevations:

| Site Identifier | Region Name | Latitude | Longitude (East) | Elevation | Primary NASA Source Reference |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `connecting_ridge` | **Connecting Ridge (Site 01)** | -89.46°S | 222.51°E (137.49°W) | +1,935.6 m | NASA PGDA Product 78 / Barker et al. (2021) Site 01 LDEM |
| `peak_near_shackleton`| **Peak Near Shackleton (Site 07)**| -88.81°S | 123.69°E | +1,647.6 m | NASA PGDA Product 78 / Barker et al. (2021) Site 07 LDEM |
| `malapert_massif` | **Malapert Massif** | -85.99°S | 357.07°E (2.93°W) | +4,843.3 m | NASA Artemis III Candidate Regions / USGS LGRS |
| `haworth` | **Haworth Crater Region** | -87.45°S | 354.83°E (5.17°W) | -3,312.3 m | NASA Artemis III Candidate Regions / IAU Gazetteer (USGS) |

---

## 4. Complete File Inventory & Architecture

Every file in the repository serves a distinct, modular purpose in the data ingestion, precomputation, user interface, or verification pipeline:

```
nasa_sapce_apps/
├── index.html                     # Main interactive web application & simulation engine
├── method.html                    # Open Science documentation, validation benchmarks & credits
├── README.md                      # Public project repository overview & quickstart
├── AI_USAGE.md                    # Official NASA Space Apps AI usage disclosure statement
├── PROJECT_REPORT.md              # Comprehensive architecture, features & presentation report
├── fetch_horizons.py              # Automated ingestion script for NASA/JPL Horizons API
├── data_pipeline/
│   └── build_horizon_profile.py   # Ray-marching algorithm for 80m LOLA DEM topography
├── docs/
│   └── DATA_SOURCES.md            # Detailed scientific data registry and query specifications
├── data/
│   ├── index.json                 # Site manifest, time windows, and coordinate metadata
│   ├── connecting_ridge.json      # 9,481 hourly Sun/Earth ephemerides for Connecting Ridge
│   ├── peak_near_shackleton.json  # 9,481 hourly Sun/Earth ephemerides for Peak Near Shackleton
│   ├── malapert_massif.json       # 9,481 hourly Sun/Earth ephemerides for Malapert Massif
│   ├── haworth.json               # 9,481 hourly Sun/Earth ephemerides for Haworth Crater
│   ├── horizon_connecting_ridge.json       # 360° ray-marched horizon elevation mask
│   ├── horizon_peak_near_shackleton.json   # 360° ray-marched horizon elevation mask
│   ├── horizon_malapert_massif.json        # 360° ray-marched horizon elevation mask
│   ├── horizon_haworth.json                # 360° ray-marched horizon elevation mask
│   └── raw/
│       └── LDEM_80S_80MPP_ADJ.TIF          # Official NASA LRO LOLA 80 m/px polar DEM GeoTIFF
├── vendor/
│   ├── three.min.js               # Standalone Three.js 3D WebGL graphics library (r128)
│   └── OrbitControls.js           # Three.js camera interaction and navigation module
└── assets/
    ├── lroc_color_2k.jpg          # NASA SVS 2K Lunar Reconnaissance Orbiter surface texture
    ├── team_logo.png              # Official Team VOIDBRONE project emblem
    ├── spacecraft.png             # Illustrative Apollo Lunar Module graphic
    ├── sun.png                    # Solar disc graphic with corona
    ├── earth.png                  # Earth disc graphic
    ├── moon.jpg                   # Lunar surface graphic (About section)
    ├── blue_moon.jpg              # Blue-tinted lunar surface graphic
    └── blue_moon.png              # Transparent blue-tinted lunar surface graphic (Strengths)
```

### 4.1 Detailed File Roles

#### Application Core
* **`index.html`**:
  The primary single-page web application. Contains the complete HTML, CSS, and client-side JavaScript for the mission simulator. It renders the HUD, controls, 3D WebGL Moon globe, the interactive heatmap matrix (Landing Window Atlas), 2D sky horizon profile, decision scoreboards, mission simulator charts, explainability modules, and the polar window minigame. It operates 100% statically without external backend servers.
* **`method.html`**:
  A dedicated static page designed to maintain Open Science integrity. It houses the **Validation Benchmark Comparison**, **Automated Browser Sanity Checks**, **Data Sources & Mathematical Methodology**, **Assumptions & Limitations**, **Strengths**, **User Personas**, and the complete **Asset & Licence Credits Table**. It is accessible directly from the top navigation and hero section.

#### Documentation & Governance
* **`README.md`**:
  The repository's front page, containing project overview, site tables, quickstart guide, local server instructions (`python -m http.server 8000`), and links to `method.html`.
* **`AI_USAGE.md`**:
  The formal disclosure required by NASA Space Apps Challenge detailing how AI assistants were utilized (for UI refactoring, boilerplate generation, and debugging), verifying that all ephemerides and terrain heights come from genuine NASA datasets with human verification.
* **`docs/DATA_SOURCES.md`**:
  A technical scientific registry documenting query parameters for the JPL Horizons API (`CENTER='coord@301'`, `COMMAND='10'`, `COMMAND='399'`, `STEP_SIZE='1 h'`), datum details (`IAU:30135`), DEM specs, and projection formulas.

#### Pipeline & Algorithms
* **`fetch_horizons.py`**:
  A Python 3 utility that interfaces with the NASA/JPL Horizons REST API (`https://ssd.jpl.nasa.gov/api/horizons.api`). It requests apparent azimuth and elevation in 90-day batches across 13 months (2026-12-01 to 2027-12-31) for all four Artemis candidate sites, parses the CSV output, and structures it into JSON format.
* **`data_pipeline/build_horizon_profile.py`**:
  The ray-marching algorithm that processes the 231 MB LRO LOLA polar digital elevation model (`LDEM_80S_80MPP_ADJ.TIF`). For each candidate site, it casts rays outward from 0° to 359° in 1° azimuth increments up to 30 km distance, calculating the maximum elevation angle while subtracting the lunar spherical curvature drop $\Delta z = d^2 / (2R)$.

#### Scientific Data Files (`data/`)
* **`data/index.json`**:
  Index file listing the evaluated sites, ephemeris duration, file mappings, and start date metadata.
* **`data/<site_id>.json`**:
  Precomputed authentic ephemeris files. Each file contains 9,481 hourly points with parallel arrays: `sun_az` (azimuth), `sun_el` (elevation), `earth_az`, `earth_el`, and ISO timestamps (`times`).
* **`data/horizon_<site_id>.json`**:
  Precomputed 360-element array of maximum topographic elevation angles (in degrees) for every azimuth from 0° to 359°.

#### Libraries & Assets
* **`vendor/three.min.js` & `vendor/OrbitControls.js`**:
  Local offline builds of Three.js (r128). Eliminates external CDN dependencies, ensuring Horizon Atlas works offline in air-gapped environments or local servers.
* **`assets/`**:
  All visual assets utilized by the application, including the high-resolution NASA LROC global color/relief texture map (`lroc_color_2k.jpg`), team branding, and illustrative diagrams.

---

## 5. Comprehensive Feature Breakdown

Horizon Atlas is packed with **nine distinct, interconnected modules**, all powered by the same underlying calculation engine:

```
┌────────────────────────────────────────────────────────────────────────┐
│                              HORIZON ATLAS                             │
│                  Lunar Landing Site Navigator Platform                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    │                               │                               │
┌───▼─────────────────────┐ ┌───────▼─────────────────────┐ ┌───────▼─────────────────────┐
│ 01. 3D MOON GLOBE       │ │ 02. LANDING WINDOW ATLAS    │ │ 03. SKY VIEW & HORIZON      │
│ • JPL Horizons Sun/Earth│ │ • 4 Sites x 24 Start Dates  │ │ • 360° LOLA Horizon Mask    │
│ • 10-Day Timeline Slider│ │ • Instant Heatmap Filtering │ │ • Solar/Earth Ray Tracing   │
│ • Off-Screen Edge Badges│ │ • Real vs Demo Mode Toggle  │ │ • 240-Hour Telemetry Strips │
└───┬─────────────────────┘ └───────┬─────────────────────┘ └───────┬─────────────────────┘
    │                               │                               │
    ├───────────────────────────────┼───────────────────────────────┤
    │                               │                               │
┌───▼─────────────────────┐ ┌───────▼─────────────────────┐ ┌───────▼─────────────────────┐
│ 04. DECISION MODE       │ │ 05. SCENARIO SIMULATOR      │ │ 06. EXPLAINABLE DECISIONS   │
│ • Multi-Criteria Weights│ │ • Battery Charge / Drain    │ │ • Score Contribution Bars  │
│ • Top 3 Shortlist       │ │ • Fatal Hour Diagnostic     │ │ • Temporal What-If Bounds   │
│ • Certainty & Slope Test│ │ • Custom Lander Assumptions │ │ • Sensitivity Diagnostic    │
└───┬─────────────────────┘ └───────┬─────────────────────┘ └───────┬─────────────────────┘
    │                               │                               │
    ├───────────────────────────────┼───────────────────────────────┤
    │                               │                               │
┌───▼─────────────────────┐ ┌───────▼─────────────────────┐ ┌───────▼─────────────────────┐
│ 07. SCIENTIST TOOLS     │ │ 08. FLIGHT SIMULATOR GAME   │ │ 09. VALIDATION & BENCHMARKS │
│ • Topographic Offsets   │ │ • Scout & Launch Gameplay   │ │ • LOLA Gläser 2014 Comparison│
│ • Full CSV Data Export  │ │ • Battery Survival Mechanics│ │ • 3 Automated Sanity Checks │
│ • Uncertainty Analysis  │ │ • Interactive Learning Mode │ │ • Plain-Language Caveats    │
└───┴─────────────────────┘ └─────────────────────────────┘ └─────────────────────────────┘
```

### Feature 1: The Interactive 3D Moon Globe
* **Authentic Astronomical Lighting**: Directional sunlight is driven directly by JPL Horizons coordinates for the currently selected landing site and mission hour. The Sun and Earth vectors are calculated in a Moon-fixed reference frame:
  $$\vec{U} = \text{normalize}(\vec{ll3}(\phi, \lambda, 1))$$
  $$\vec{E} = (-\sin\lambda, 0, -\cos\lambda)$$
  $$\vec{N} = (-\sin\phi\cos\lambda, \cos\phi, \sin\phi\sin\lambda)$$
  $$\vec{d}_{\text{celestial}} = \cos(\text{el}) \cdot (\sin(\text{az})\vec{E} + \cos(\text{az})\vec{N}) + \sin(\text{el})\vec{U}$$
* **10-Day Mission Timeline Player**: Users can scrub an hour slider (0 to 239 hours) or click Play (advancing 1 hour every 60 ms) to watch the Moon rotate, shadows stretch across the terrain, and Earth drift along the horizon.
* **Celestial Body Markers & Off-Screen Edge Badges**: Spherical markers display the apparent positions of the Sun and Earth (marked "not to scale"). If a body moves off-screen, a floating HUD edge badge indicates its direction and angular offset.
* **Interactive Landing Pins**: Pins are positioned from real geodetic coordinates (`REAL_SITES`), changing color dynamically (Green = Passes mission needs, Red = Fails). Clicking a pin immediately selects that site across the entire platform.
* **Mobile-Optimized Architecture**: Features **render-on-demand** (0% GPU/CPU utilization when idle), directional touch separation (vertical swipe scrolls the page smoothly; horizontal swipe rotates the globe), and `IntersectionObserver` auto-pausing when scrolled out of view.
* **Full-View Immersion Mode**: A single click on the `⛶` button expands the globe into an unobstructed full-screen viewport.

### Feature 2: Landing Window Atlas (The Heatmap Matrix)
* **Comprehensive Search Grid**: Displays a 4-site $\times$ 24-date matrix (96 distinct 10-day mission windows = 23,040 hours of simulation).
* **Instant Filtering**: When the user moves the Sunlight, Darkness, or Earth Contact sliders, the matrix updates instantly. Cells transition from red (far from passing) to green (meets all requirements).
* **Candidate Shortlist**: Highlights the top candidate choices meeting all criteria, or identifies the closest options if no window passes.
* **Dataset Toggle**: Allows toggling between the authentic NASA Horizons + LOLA model (4 sites) and a synthetic Demo Model (8 sites) to test edge cases.

### Feature 3: Sky View & Topographic Horizon Mask
* **360° Ray-Marched Horizon Profile**: Plots the real horizon silhouette computed from the 80m LOLA DEM.
* **Solar & Terrestrial Elevation Tracking**: Displays Sun and Earth discs against the terrain profile, indicating exact elevation and azimuth.
* **Real-Time Masking Logic**: Clearly indicates whether the Sun is unblocked or occluded by mountain ridges, and whether direct-to-Earth communication is active.
* **240-Hour Horizon Strips**: Displays color-coded dual timeline ribbons: gold for illuminated hours, electric blue for Earth-visible hours, with an active playhead scrubber.

### Feature 4: Decision Mode (Prioritization Engine)
* **Multi-Criteria Decision Analysis (MCDA)**: Mission planners assign priority weights (0 to 100) to four criteria:
  1. High Sunlight
  2. Short Darkness
  3. Continuous Earth Contact
  4. Scientific Value (PSR proximity)
* **Top 3 Shortlist**: Automatically calculates overall scores ($0-100$) and surfaces the top 3 ranked mission windows with their relative strengths and vulnerabilities.
* **Certainty Rating & Slope Offset**: Simulates what happens if local landing slope or micro-relief raises the horizon by 0.3° (~400 m offset), classifying site certainty as High, Medium, or Low.

### Feature 5: Mission Scenario Simulator
* **Battery Dynamics Modeling**: Simulates hour-by-hour battery state-of-charge over the full 240-hour mission.
* **Configurable Power Parameters**:
  - Battery drain per dark hour (0.5 to 4.0 %/h).
  - Solar recharge per sunlit hour (1.0 to 6.0 %/h).
  - Mandatory daily Earth communications requirement toggle.
* **Critical Hour Identification**: If a lander fails, the simulator identifies the exact critical failure hour and cause (e.g. *"OUT OF POWER on day 4, hour 18. That hour decided the mission"*).

### Feature 6: Explainable Decisions & Geometry
* **No Black-Box Machine Learning**: Eliminates mysterious deep learning models in favor of transparent deterministic physics.
* **Score Contribution Breakdown**: Displays horizontal contribution bars showing exactly how many points each criterion pushed the score up or down from base 50.
* **Temporal "What If..." Analysis**: Evaluates shifting the launch date by $-6, -3, +3, +6$ days or adding a 0.3° horizon obstruction. If a shifted date exceeds the available 13-month data range, it cleanly reports `no data before <date>` or `no data after <date>`, strictly avoiding duplicate clamping errors.
* **Requirement Sensitivity Diagnostic**:
  - If all criteria fail: Identifies the closest-to-passing requirement and the exact shortfall gap.
  - If some fail: Details each failing criterion and its distance from the limit.
  - If all pass: Identifies the most sensitive parameter that would flip the verdict first.

### Feature 7: Scientist Tools & Data Export
* **Landing Offset Uncertainty**: Tests horizon elevation perturbations (+0.0°, +0.15°, +0.30°, +0.50°), simulating landing displacement errors from 0 to 660 meters.
* **RFC 4180 CSV Export**: One-click export of all evaluated sites, dates, sunlight percentages, longest dark hours, and Earth contact stats, ready for Python/Pandas, MATLAB, or Excel.

### Feature 8: Flight Simulator Game (Polar Window)
* **Interactive Educational Minigame**: Translates the complex orbital simulator into an engaging gamified experience.
* **Mission Lifecycle**: Players select difficulty levels (Scout, Standard, Strict), scout prospective landing sites, launch landers, and monitor live telemetry strips to survive the lunar polar night.

### Feature 9: Scientific Validation & Sanity Checks (`method.html`)
* **NASA LOLA Illumination Benchmark**: Compares our computed 13-month sunlight percentage for Malapert Massif (7.4% with terrain mask ON; 50.1% with mask OFF) against published NASA LOLA polar illumination studies (Gläser et al. 2014, NASA PGDA Product 69).
* **Transparent Scientific Caveats**:
  - *Averaging Period*: Published models average over an 18.6-year lunar precession cycle (~163,000 hours), while Horizon Atlas models an operational 13-month mission window (9,481 hours).
  - *Observer Height*: Published benchmarks evaluate elevated masts (e.g. 2 m above surface); Horizon Atlas evaluates ground level (0 m).
  - *DEM Resolution*: Published studies use 20 m/px DEM; Horizon Atlas uses the 80 m/px polar DEM (`LDEM_80S_80MPP_ADJ`).
* **Automated Browser Sanity Checks**: Runs live in the user's browser:
  1. *Coordinate Limits & Time-Series Integrity*: Confirms all elevations lie in $[-90^\circ, +90^\circ]$ and arrays have identical lengths (9,481 points per site) $\rightarrow$ **PASS ✓**.
  2. *Topographic Mask Monotonicity*: Verifies that Terrain Mask ON never produces more sunlight than Mask OFF $\rightarrow$ **PASS ✓**.
  3. *Local Horizon Relief Plausibility*: Checks that terrain mask angles lie within realistic physical limits ($0^\circ \le \theta \le 45^\circ$) and reports per-site ranges $\rightarrow$ **PASS ✓**.

---

## 6. How to Run & Present the Project

### 6.1 Running Locally (30 Seconds)
Due to browser security restrictions on asynchronous `fetch()` for local JSON files, run a lightweight static web server from the project directory:

```bash
# 1. Open your terminal in the repository root
cd c:\Users\user\Downloads\nasa_sapce_apps

# 2. Start Python's built-in HTTP server
python -m http.server 8000
```
Then open your web browser to:
**[http://localhost:8000](http://localhost:8000)**

---

## 7. Presentation & Pitch Guide

When presenting Horizon Atlas to judges, educators, or engineers, use this structured walkthrough:

### 30-Second Elevator Pitch
> *"Landing on the lunar South Pole is notoriously difficult because mountains block sunlight and crater walls cut off communications with Earth. Traditional tools force you to test one landing site at a time. Horizon Atlas inverts the problem: you set what your lander needs to survive—how much sunlight, maximum dark hours, and Earth contact—and our platform instantly searches 13 months of real NASA/JPL Horizons ephemerides and 80-meter LRO LOLA topography to find the optimal landing site and date. It’s fully explainable, works on phone or desktop, and is built on 100% open NASA science."*

### 2-Minute Demonstration Flow
1. **The Hero & 3D Globe**: Show the 3D Moon with live solar illumination driven by real JPL Horizons data. Scrub the hour slider to show the sunlight and Earth line-of-sight changing over 10 days.
2. **The Atlas Heatmap**: Show the 4 Artemis III sites across 24 start dates. Adjust the "Sunlight at least" slider from 55% to 70% and watch the heatmap instantly re-filter all 96 landing windows.
3. **The Sky View**: Click an Atlas cell to show the 360° ray-marched horizon mask. Point out how the mountain ridge blocks the Sun while Earth remains visible.
4. **Decision & Battery Simulation**: Move down to the Scenario Simulator to show the hour-by-hour battery curve. Show how a single shadowed hour can make or break a mission.
5. **Explainability & Open Science**: Show the contribution bars and sensitivity note ("Fails all 3 requirements. Closest to passing: Sunlight need..."). Click **Validation & Method** to display our live comparison against NASA published benchmarks and automated sanity checks.

---

## 8. Summary of Technologies Used

* **Frontend**: Vanilla HTML5, Modern CSS3 (CSS Grid, Custom Variables, Mobile Compositor Optimizations), ES6+ JavaScript (Async/Await, Canvas API, SVG generation).
* **3D Graphics Engine**: Three.js (r128), OrbitControls, Phong Material Shaders, Texture Mapping, Raycasting.
* **Astronomical & Geospatial Data Pipeline**: Python 3, NASA/JPL Horizons REST API, GDAL/Rasterio, NumPy, South Polar Stereographic Projection (`IAU:30135`).
* **Compliance & Standards**: NASA Open Science, RFC 4180 CSV, Zero Third-Party CDN Runtime Dependencies (100% Local Vendor Hosting).
