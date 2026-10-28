# Limitations

Maintain a living record of data gaps, imagery differences, georeferencing uncertainty, classification uncertainty, licensing constraints, scope limitations, and interpretations that are not supported by the available evidence.

## 79-settlement screening (2026-10-02)

- **Selection proxy:** one building-density-selected settlement per local level. It may not be the
  municipal headquarters, and it ignores other exposed settlements in the same local level. 14 of 79
  rely on the densest-building-cluster fallback (lower confidence).
- **Mapped drainage only:** streams missing from OSM are absent from HAND, so exposure along them is
  under-estimated. Where OSM channels are offset from the DEM valley, the 5 m burn may route flow
  incorrectly.
- **DEM:** GLO-30 vertical error is metres in steep terrain, comparable to the 2–10 m scenario levels.
  It reflects 2011–2015 terrain and tree and building heights (it is a surface model, not bare earth).
- **Not a flood model:** HAND zones have no frequency, depth, velocity or timing. Debris flows, GLOFs,
  landslide-dam outbursts and bank erosion, which are important in Karnali, are not represented.
- **Buildings ≠ people:** footprints mix sources and dates. No population or occupancy is used, so no
  statement about lives at risk is possible from these outputs alone.
- **Imagery comparability:** sensors, resolutions (60/30/10 m), seasons and sun angles differ. 1970s MSS
  cannot resolve buildings. Some epochs have no usable dry-season scene (for example, no 1980–84 scenes
  exist over some sites). Snow-covered or partly cloudy chips are shown only when nothing better exists,
  with the fraction recorded.
- **GHSL:** a modelled ~90 m product. Small rural settlements may be under-detected, and its 1975–1985
  epochs are back-cast by the producer.
- **Urban/rural type:** taken from a secondary source (Wikipedia citing MoFALD), not checked against the
  current MoFAGA register.

## Live monitoring layer (2026-10-02)

- **Not an early-warning system.** No threshold has been validated against events. Rain categories
  are IMD terms used as labels. The river and radar ratios are relative indicators with no hydrological
  calibration.
- **Model values:** rain and discharge are model output. GloFAS cells (~5 km) can represent a larger
  river than the khola next to a settlement.
- **Radar water** (VV < −18 dB) can be confused with smooth surfaces such as fresh tarmac and dry sand,
  and with radar shadow. Measuring only inside the HAND ≤ 10 m zone reduces but does not remove this.
  Ratios need several passes to mean anything.
- **Optical water** (MNDWI > 0) is counted only on clear pixels. Cloud and terrain shadow remain error
  sources.
- **BIPAD incidents** are as reported, with variable completeness and location accuracy. The nearest
  settlement is assigned by distance, not by verified impact.
- **Latency:** satellite passes every few days and are processed within hours; rain hourly; incidents
  as reported.
