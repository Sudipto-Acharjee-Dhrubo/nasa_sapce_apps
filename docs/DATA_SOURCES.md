# NASA Data Sources – Horizon Atlas

This document registers every NASA open dataset utilized in **Horizon Atlas** (`CLPS Lunar Mission Browser`, NASA Space Apps Challenge 2026). In accordance with NASA Open Science guidelines and competition rules, all data sources, endpoints, parameters, and processing pipelines are explicitly documented.

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

## 2. Lunar Surface Topography (LRO LOLA)

| Parameter | Specification |
| :--- | :--- |
| **Dataset Name** | Lunar Reconnaissance Orbiter (LRO) Lunar Orbiter Laser Altimeter (LOLA) Digital Elevation Model (DEM) |
| **Provider** | NASA Planetary Geodynamics Data Archive (PGDA) / LOLA Science Team |
| **Product Nodes** | [https://pgda.gsfc.nasa.gov/products/90](https://pgda.gsfc.nasa.gov/products/90) (South Pole DEMs, >80°S)<br>[https://imbrium.mit.edu/](https://imbrium.mit.edu/) (LOLA Data Node)<br>[https://pgda.gsfc.nasa.gov/products/78](https://pgda.gsfc.nasa.gov/products/78) (High-Resolution Site DEMs) |
| **Target Files** | `LDEM_80S_80MPP_ADJ.TIF` (80 m/pixel, South Polar Stereographic) |
| **Projection & Datum** | Polar Stereographic, center latitude -90°, center longitude 0°, reference radius 1737.4 km |
| **Vertical Reference**| Elevation in meters relative to 1737.4 km lunar sphere |
| **Date Accessed** | November 2026 |
| **Processing** | Executed via `data_pipeline/build_horizon_profile.py`. Converts geographic lunar coordinates to polar stereographic coordinates, crops local elevation bounding box around target landing sites, and executes radial ray-marching across 360° azimuth (1° steps) accounting for lunar curvature to derive maximum horizon elevation angles. |
| **Usage in Project** | Constructs local 360° terrain horizon masks (`data/horizon_<site>.json`) to determine when topography (crater rims, ridges, massifs) blocks direct solar illumination or Earth line-of-sight. |

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

