# NASA Data Sources – Horizon Atlas

This document registers every NASA open dataset utilized in **Horizon Atlas** (`Lunar Landing Site Navigator`, NASA Space Apps Challenge 2026). In accordance with NASA Open Science guidelines and competition rules, all data sources, endpoints, parameters, and processing pipelines are explicitly documented.

---

## 1. Sun and Earth Ephemerides

| Parameter | Specification |
| :--- | :--- |
| **Dataset Name** | NASA / JPL Horizons On-Line Solar System Data Service |
| **Provider** | Solar System Dynamics Group, Jet Propulsion Laboratory (NASA / Caltech) |
| **Access URL** | [https://ssd.jpl.nasa.gov/api/horizons.api](https://ssd.jpl.nasa.gov/api/horizons.api) |
| **Web Interface** | [https://ssd.jpl.nasa.gov/horizons/](https://ssd.jpl.nasa.gov/horizons/) |
| **Date Accessed** | November 2026 |
| **Target Bodies** | Sun (`COMMAND='10'`), Earth (`COMMAND='399'`) |
| **Observer Center** | Lunar Geodetic Surface Coordinate (`CENTER='coord@301'`, `COORD_TYPE='GEODETIC'`) |
| **Quantities** | Apparent Azimuth and Elevation (`QUANTITIES='4'`), Angle Format: Degrees (`ANG_FORMAT='DEG'`) |
| **Time Step** | Hourly (`STEP_SIZE='1 h'`) over mission windows |
| **Processing** | Queried via `fetch_horizons.py`; parsed CSV ephemeris tables to extract hourly apparent azimuth and elevation relative to the local geometric horizon of the reference ellipsoid/sphere. Output saved to `data/<site>.json`. |
| **Usage in Project** | Provides authentic astronomical positions of the Sun (for solar power assessment) and Earth (for direct line-of-sight communications). |

---

## 1.1 Target Artemis III Candidate Landing Sites & Coordinates

All coordinates are derived strictly from official NASA publication databases and LRO LOLA landing site cartography products (no invented coordinates):

| Site Key | Candidate Region Name | Latitude (°N/S) | Longitude (°E) | Alt (km) | Official NASA Source & Reference |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `connecting_ridge` | Connecting Ridge (Site 01) | -89.46° | 222.51° (-137.49°) | 0.0 | **NASA PGDA Product 78** / Barker et al. (2021), *Planetary and Space Science* 203, 105119 (Site 01 LDEM). [https://pgda.gsfc.nasa.gov/products/78](https://pgda.gsfc.nasa.gov/products/78) |
| `peak_near_shackleton` | Peak Near Shackleton (Site 07) | -88.81° | 123.69° | 0.0 | **NASA PGDA Product 78** / Barker et al. (2021), *Planetary and Space Science* 203, 105119 (Site 07 LDEM). [https://pgda.gsfc.nasa.gov/products/78](https://pgda.gsfc.nasa.gov/products/78) |
| `malapert_massif` | Malapert Massif | -85.99° | 357.07° (-2.93°) | 0.0 | **NASA Artemis III Candidate Regions** (NASA GSFC / USGS LGRS cartographic benchmarks). [https://www.nasa.gov/news-release/nasa-identifies-candidate-regions-for-landing-next-americans-on-Moon/](https://www.nasa.gov/news-release/nasa-identifies-candidate-regions-for-landing-next-americans-on-Moon/) |
| `haworth` | Haworth Crater Region | -87.45° | 354.83° (-5.17°) | 0.0 | **NASA Artemis III Candidate Regions** / IAU Gazetteer of Planetary Nomenclature, USGS Astrogeology. [https://planetarynames.wr.usgs.gov/Feature/2390](https://planetarynames.wr.usgs.gov/Feature/2390) |

---

## 2. Lunar Surface Topography (LRO LOLA)

| Parameter | Specification |
| :--- | :--- |
| **Dataset Name** | Lunar Reconnaissance Orbiter (LRO) Lunar Orbiter Laser Altimeter (LOLA) Digital Elevation Model (DEM) |
| **Provider** | NASA Planetary Geodynamics Data Archive (PGDA) / LOLA Science Team (NASA GSFC / MIT) |
| **Product Nodes** | [https://pgda.gsfc.nasa.gov/products/90](https://pgda.gsfc.nasa.gov/products/90) (South Pole DEMs, >80°S)<br>[https://imbrium.mit.edu/](https://imbrium.mit.edu/) (LOLA Data Node)<br>[https://pgda.gsfc.nasa.gov/products/78](https://pgda.gsfc.nasa.gov/products/78) (High-Resolution Site DEMs) |
| **Target Files** | `LDEM_80S_80MPP_ADJ.TIF` (7600 x 7600 pixels, 80.0 m/pixel resolution, float32) |
| **Projection & Datum** | Moon (2015) South Polar Stereographic (`IAU:30135`), center latitude -90°, center longitude 0°, reference radius 1737.4 km |
| **Vertical Reference**| Elevation in meters relative to 1737.4 km reference lunar sphere |
| **Ray-Marching Parameters** | Max distance: 30 km (30,000 m); Step size: 80 m (matching pixel resolution); Azimuth range: 0° to 359° in 1° steps; Observer height: 0.0 m (ground level) |
| **Lunar Curvature Drop** | $\Delta z = (h_{\text{terrain}} - h_{\text{observer}}) - \frac{d^2}{2R}$, with $R = 1737.4\text{ km}$ |
| **Date Accessed** | November 2026 |
| **Processing** | Executed via `data_pipeline/build_horizon_profile.py`. Projects geodetic landing site coordinates to DEM polar stereographic raster coordinates, evaluates ground elevation, and marches radially along 360 azimuth rays outward to 30 km. For each ray, the maximum terrain elevation angle above the local tangent plane is computed and saved to `data/horizon_<site>.json`. |
| **Horizon Stats** | - Connecting Ridge: Min 0.00°, Mean 3.83°, Max 7.80°<br>- Peak Near Shackleton: Min 0.00°, Mean 0.00°, Max 0.01°<br>- Malapert Massif: Min 0.00°, Mean 4.12°, Max 15.90°<br>- Haworth: Min 3.65°, Mean 8.83°, Max 12.34° |
| **Usage in Project** | Provides authentic local topographic horizon elevation profiles used to mask solar illumination and Earth line-of-sight in `index.html`. |

---

## 3. Published Polar Illumination Maps (Validation Reference)

| Parameter | Specification |
| :--- | :--- |
| **Dataset Name** | Lunar Polar Illumination and Earth Visibility Maps |
| **Provider** | NASA Goddard Space Flight Center / NASA PGDA |
| **Access URL** | [https://pgda.gsfc.nasa.gov/products/69](https://pgda.gsfc.nasa.gov/products/69) |
| **Reference Paper** | Gläser, P., et al. (2014), *Illumination conditions at the lunar poles: Implications for future exploration*, Icarus, 243, 78–90. [doi:10.1016/j.icarus.2014.08.013](https://doi.org/10.1016/j.icarus.2014.08.013) |
| **Usage in Project** | Independent benchmark to validate Horizon Atlas computed illumination percentages against published peer-reviewed LOLA illumination models. |

---

## 4. Open Portals & Verification

- NASA Open Data Portal: [https://data.nasa.gov](https://data.nasa.gov)
- NASA Open APIs: [https://api.nasa.gov](https://api.nasa.gov)
- NASA Commercial Lunar Payload Services (CLPS): [https://www.nasa.gov/clps](https://www.nasa.gov/clps)

