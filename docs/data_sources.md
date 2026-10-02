# Data sources

For every source, record provider, URL or citation, license, acquisition date, temporal coverage, spatial resolution, CRS, download or access method, checksum where applicable, and redistribution restrictions.

## Sources used by the 79-settlement screening (accessed 2026-10-02)

| Source | Provider | Access | Licence | Coverage / resolution | Use |
|---|---|---|---|---|---|
| COD-AB Nepal subnational boundaries (`npl_admin_boundaries.gdb`, admin3, valid_on 2024-03-14) | Survey Department of Nepal; UN RCO Nepal; OCHA HDX `cod-ab-npl` | HDX download (cached, not committed) | CC BY-IGO | 753+ local units, vector | 79 Karnali local levels; simplified copy in `data/processed/karnali_79/` |
| Local-level urban/rural type | Wikipedia "Administration in Karnali Province" citing MoFALD register | web page, raw wikitext | CC BY-SA 4.0 (text) | 25 municipalities listed | `local_level_type` |
| Overture Maps `divisions/locality` | Overture Maps Foundation, release 2026-09-23.1 (from OpenStreetMap) | S3 GeoParquet via DuckDB, bbox query | ODbL | points | candidate settlements and names |
| Overture Maps `base/water` | Overture (OpenStreetMap) | as above | ODbL | lines/polygons | rivers and streams for HAND |
| Overture Maps `buildings` | Overture (OSM 1.21 M, Google Open Buildings 0.52 M, Microsoft ML Buildings 0.26 M in bbox) | as above | ODbL / CC BY 4.0 | footprints → centroids | settlement selection, exposure counts |
| Copernicus DEM GLO-30 | ESA / Airbus, via Microsoft Planetary Computer `cop-dem-glo-30` | COG streaming | Copernicus DEM licence (free, attribution) | 30 m, 2011–2015 acquisition | HAND |
| Landsat Collection 2 L1 (MSS) and L2 (TM/ETM+/OLI) | USGS, via Planetary Computer | COG streaming | public domain | 1972–present, 60/30 m | image time series |
| Sentinel-2 L2A | ESA Copernicus, via Planetary Computer | COG streaming | Copernicus Sentinel data terms | 2015–present, 10 m | image time series, scenario base map |
| GHS-BUILT-S R2023A, 4326 3″ tiles R6_C27 and R7_C27 | European Commission JRC | HTTPS tiles, cropped to Karnali | CC BY 4.0 | 1975–2020 in 5-year epochs, ~90 m | built-up surface history |

Raw inputs are kept outside Git in a disposable cache (`$KARNALI_CACHE`) and are re-creatable with
`src/data/fetch_karnali_inputs.py`. Only derived layers, figures and tables are committed.

## Near-real-time sources (dashboard Live layer, from 2026-10-02)

| Source | Provider | Access | Licence / terms | Notes |
|---|---|---|---|---|
| Hourly precipitation, past and forecast | Open-Meteo (blend of national weather models) | `api.open-meteo.com/v1/forecast`, no key | CC BY 4.0; free for non-commercial use | Model values, not gauges |
| River discharge (GloFAS v4) | Copernicus EMS GloFAS via Open-Meteo flood API | `flood-api.open-meteo.com/v1/flood` | CC BY 4.0 | ~5 km cells; small kholas not resolved |
| Disaster incidents | BIPAD portal, NDRRMA / Government of Nepal | `bipadportal.gov.np/api/v1/incident/` | Public API; terms not stated (unknown); cite BIPAD | Filtered to Karnali (province 6) and water-related hazards |
| Sentinel-1 RTC | ESA Copernicus; RTC processing by Microsoft Planetary Computer | STAC `sentinel-1-rtc` | Copernicus terms; RTC product © Microsoft, CC BY 4.0 | 10 m radar, about every 3–6 days over Karnali |
| NASA GIBS layers (VIIRS, MODIS, HLS, OPERA DSWx, IMERG, DIST-ALERT, MODIS flood) | NASA EOSDIS | WMTS tiles, no key | NASA open data (no restrictions; attribution requested) | Display only |
| Basemaps | OpenStreetMap, HOT, CyclOSM, OpenTopoMap, Esri, EOX | XYZ tiles | Per provider (OSM ODbL; OpenTopoMap CC BY-SA; EOX s2cloudless 2023 CC BY-NC-SA 4.0; Esri terms for non-commercial display) | Display only, not redistributed |
| JRC Global Surface Water | European Commission JRC | XYZ tiles | CC BY 4.0 | Water occurrence 1984–2021 |
| DHM real-time hydro-met | Department of Hydrology and Meteorology | API requires a key | unknown | Not used yet |
