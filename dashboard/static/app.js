/* Karnali Settlement Explorer: frontend (vanilla JS + Leaflet + Chart.js). */
"use strict";

const REPO = "https://github.com/iamhbc/karnali-settlement-hazard-mapping/blob/main/";
const S = { list: [], sel: null, detail: null, images: [], charts: {}, compare: { a: null, b: null, mode: "side" },
            timelineStep: 5, activeTab: "timeline", provinceLoaded: false };

const $ = (q, el = document) => el.querySelector(q);
const $$ = (q, el = document) => [...el.querySelectorAll(q)];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (v, d = 0) => (v === null || v === undefined || Number.isNaN(v)) ? "–" : Number(v).toLocaleString(undefined, { maximumFractionDigits: d, minimumFractionDigits: d });
const pctf = (v, d = 1) => (v === null || v === undefined) ? "–" : `${(v * 100).toFixed(d)}%`;
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const api = async (path) => {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  return path.endsWith("/profile") ? r.text() : r.json();
};
const debounce = (fn, ms = 200) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };

/* ---------------- map ---------------- */
const map = L.map("map", { zoomControl: true, preferCanvas: true }).setView([29.1, 82.2], 7);
/* Base maps and overlays: every open/free tile service verified on 2026-10-02 (no API keys). */
const T = (url, attribution, o = {}) => L.tileLayer(url, { attribution, maxZoom: 19, ...o });
const ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services";
const base = {
  "Light grey (Esri)": T(`${ESRI}/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}`, "Tiles © Esri — Esri, HERE, Garmin, © OpenStreetMap contributors", { maxZoom: 16 }),
  "OpenStreetMap": T("https://tile.openstreetmap.org/{z}/{x}/{y}.png", "© OpenStreetMap contributors"),
  "OSM Humanitarian (HOT)": T("https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png", "© OpenStreetMap contributors, tiles HOT / OSM France"),
  "CyclOSM (roads & trails)": T("https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png", "© OpenStreetMap contributors, CyclOSM"),
  "OpenTopoMap (contours)": T("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", "© OpenStreetMap contributors, SRTM | © OpenTopoMap (CC BY-SA)", { maxZoom: 17 }),
  "Esri World Topographic": T(`${ESRI}/World_Topo_Map/MapServer/tile/{z}/{y}/{x}`, "Tiles © Esri and contributors"),
  "Esri NatGeo": T(`${ESRI}/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}`, "Tiles © Esri, National Geographic", { maxZoom: 16 }),
  "EOX Terrain": T("https://tiles.maps.eox.at/wmts/1.0.0/terrain-light_3857/default/GoogleMapsCompatible/{z}/{y}/{x}.jpg", "Terrain © EOX IT Services, © OpenStreetMap contributors", { maxZoom: 15 }),
  "Satellite: Esri World Imagery (high-res)": T(`${ESRI}/World_Imagery/MapServer/tile/{z}/{y}/{x}`, "Imagery © Esri, Maxar, Earthstar Geographics"),
  "Satellite: Sentinel-2 cloudless 2023 (EOX)": T("https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2023_3857/default/GoogleMapsCompatible/{z}/{y}/{x}.jpg", "Sentinel-2 cloudless 2023 © EOX IT Services (contains modified Copernicus Sentinel data 2023), CC BY-NC-SA 4.0", { maxZoom: 15 }),
};
base["Light grey (Esri)"].addTo(map);
const overlays = {
  "Local levels (79)": null,   // filled below
  "Place labels (Esri)": T(`${ESRI}/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}`, "Labels © Esri"),
  "Hillshade (Esri)": T(`${ESRI}/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}`, "Hillshade © Esri", { opacity: 0.45 }),
  "Water occurrence 1984-2021 (JRC GSW)": T("https://storage.googleapis.com/global-surface-water/tiles2021/occurrence/{z}/{x}/{y}.png", "JRC Global Surface Water (Pekel et al. 2016), CC BY 4.0", { maxNativeZoom: 13 }),
};
const layers = { levels: L.geoJSON(null), markers: L.layerGroup().addTo(map), zones: {}, window: L.layerGroup().addTo(map), scene: null, gibs: {} };
overlays["Local levels (79)"] = layers.levels;
const ctrl = L.control.layers(base, overlays, { collapsed: true }).addTo(map);

/* NASA GIBS near-real-time layers (daily or 30-min), with a date picker for the daily ones. */
const GIBS = {
  "VIIRS_NOAA20_CorrectedReflectance_TrueColor": ["Satellite today: VIIRS NOAA-20 true colour (daily, 375 m)", "base"],
  "VIIRS_NOAA21_CorrectedReflectance_TrueColor": ["Satellite today: VIIRS NOAA-21 true colour (daily, 375 m)", "base"],
  "MODIS_Terra_CorrectedReflectance_TrueColor": ["Satellite today: MODIS Terra true colour (daily, 250 m)", "base"],
  "HLS_S30_Nadir_BRDF_Adjusted_Reflectance": ["Satellite: HLS Sentinel-2 (30 m, by date)", "base"],
  "HLS_L30_Nadir_BRDF_Adjusted_Reflectance": ["Satellite: HLS Landsat (30 m, by date)", "base"],
  "OPERA_L3_Dynamic_Surface_Water_Extent-Sentinel-1": ["Surface water from radar: OPERA DSWx-S1 (30 m, by date)", "overlay"],
  "OPERA_L3_Dynamic_Surface_Water_Extent-HLS": ["Surface water from optical: OPERA DSWx-HLS (30 m, by date)", "overlay"],
  "MODIS_Combined_Flood_3-Day": ["Flood: MODIS 3-day flood map (250 m)", "overlay"],
  "IMERG_Precipitation_Rate_30min": ["Rain now: GPM IMERG rate (latest 30 min)", "overlay"],
  "OPERA_L3_DIST-ALERT-HLS_Color_Index": ["Land disturbance alerts: OPERA DIST-ALERT (30 m)", "overlay"],
};
let gibsMeta = {};
const gibsUrl = (id, t) => { const m = gibsMeta[id]; const ext = m.format.endsWith("png") ? "png" : "jpg";
  return `https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/${id}/default/${t}/${m.matrix_set}/{z}/{y}/{x}.${ext}`; };
const dateCtl = L.control({ position: "topright" });
dateCtl.onAdd = () => {
  const d = L.DomUtil.create("div", "legend datectl");
  d.innerHTML = `<label class="small">NASA daily layers date <input type="date" id="gibs-date"></label>`;
  L.DomEvent.disableClickPropagation(d);
  return d;
};
async function initGibs() {
  try { gibsMeta = await api("/api/gibs/latest"); } catch { return; }
  dateCtl.addTo(map);
  const latestDay = Object.entries(gibsMeta).filter(([k]) => k.startsWith("VIIRS")).map(([, v]) => v.default).sort().at(-1);
  const inp = $("#gibs-date"); inp.value = latestDay; inp.max = latestDay;
  for (const [id, [label, kind]] of Object.entries(GIBS)) {
    const m = gibsMeta[id]; if (!m) continue;
    const t = id.includes("30min") ? m.default : (id.startsWith("VIIRS") || id.startsWith("MODIS") ? latestDay : m.default);
    const lyr = L.tileLayer(gibsUrl(id, t), { maxNativeZoom: m.max_zoom, maxZoom: 19, opacity: kind === "overlay" ? 0.85 : 1,
      attribution: `NASA GIBS / EOSDIS (${id.split("_")[0]})` });
    lyr._gibsId = id;
    layers.gibs[id] = lyr;
    kind === "base" ? ctrl.addBaseLayer(lyr, label) : ctrl.addOverlay(lyr, label);
  }
  inp.addEventListener("change", () => {
    for (const [id, lyr] of Object.entries(layers.gibs)) if (!id.includes("30min")) lyr.setUrl(gibsUrl(id, inp.value));
  });
}

/* Full-resolution view of one exact scene (Planetary Computer tiler). */
async function showSceneOnMap(collection, item, label) {
  try {
    const tj = await api(`/api/tilejson?collection=${encodeURIComponent(collection)}&item=${encodeURIComponent(item)}`);
    if (layers.scene) { map.removeLayer(layers.scene); ctrl.removeLayer(layers.scene); }
    layers.scene = L.tileLayer(tj.tiles[0], { maxZoom: 19, maxNativeZoom: tj.maxzoom || 18, bounds: tj.bounds ? [[tj.bounds[1], tj.bounds[0]], [tj.bounds[3], tj.bounds[2]]] : undefined,
      attribution: "Scene via Microsoft Planetary Computer" }).addTo(map);
    ctrl.addOverlay(layers.scene, `Scene: ${label}`);
    layers.markers.bringToFront?.();
  } catch (e) { alert(`Could not load scene tiles: ${e.message}`); }
}

const legend = L.control({ position: "bottomleft" });
legend.onAdd = () => {
  const d = L.DomUtil.create("div", "legend");
  d.innerHTML = `<b>Settlements</b><br><i style="background:${css("--marker")}"></i>size = buildings HAND ≤ 5 m<br>
    <i style="background:${css("--marker")};outline:2px solid ${css("--text-primary")}"></i>urban municipality (dark ring)<br>
    <b>Low ground (selected)</b><br>
    <i class="sq" style="background:${css("--zone-2")}"></i>HAND ≤ 2 m
    <i class="sq" style="background:${css("--zone-5")};margin-left:6px"></i>≤ 5 m
    <i class="sq" style="background:${css("--zone-10")};margin-left:6px"></i>≤ 10 m`;
  return d;
};
legend.addTo(map);

function drawMarkers() {
  layers.markers.clearLayers();
  for (const s of S.list) {
    const m = L.circleMarker([s.lat, s.lon], {
      radius: 4 + Math.min(Math.sqrt(s.buildings_le_5m) * 0.3, 16),
      color: s.local_level_type.startsWith("urban") ? css("--text-primary") : css("--surface-1"),
      weight: s.local_level_type.startsWith("urban") ? 2.5 : 1.5,
      fillColor: css("--marker"), fillOpacity: s.settlement_id === S.sel ? 1 : 0.8,
    });
    m.bindTooltip(`<b>${esc(s.settlement_id)} ${esc(s.name)}</b><br>${esc(s.local_level)} (${esc(s.local_level_type)}), ${esc(s.district)}<br>
      Buildings: ${fmt(s.buildings_in_window)} · HAND ≤ 5 m: ${fmt(s.buildings_le_5m)} (${pctf(s.share_le_5m)})<br>Exposure rank ${s.exposure_rank} / 79`);
    m.on("click", () => select(s.settlement_id));
    m.addTo(layers.markers);
  }
}

async function drawZones(sid) {
  for (const l of Object.values(layers.zones)) map.removeLayer(l);
  layers.zones = {};
  const z = await api(`/api/settlements/${sid}/zones`);
  for (const h of [10, 5, 2]) {
    layers.zones[h] = L.geoJSON(z[h], { style: { color: css(`--zone-${h}`), weight: 0, fillColor: css(`--zone-${h}`), fillOpacity: 0.5 } });
    if ($(`input[data-zone="${h}"]`).checked) layers.zones[h].addTo(map);
  }
}

function drawWindow(d) {
  layers.window.clearLayers();
  const dl = 2000 / 111320, dn = 2000 / (111320 * Math.cos(d.lat * Math.PI / 180));
  L.rectangle([[d.lat - dl, d.lon - dn], [d.lat + dl, d.lon + dn]],
    { color: css("--text-primary"), weight: 1.5, dashArray: "4 4", fill: false, interactive: false }).addTo(layers.window);
}

/* ---------------- list ---------------- */
async function loadList() {
  const p = new URLSearchParams({ q: $("#search").value, district: $("#f-district").value, type: $("#f-type").value, sort: $("#f-sort").value });
  S.list = await api(`/api/settlements?${p}`);
  $("#list-count").textContent = `${S.list.length} of 79 settlements`;
  $("#list").innerHTML = S.list.map((s) => `
    <li data-id="${s.settlement_id}" class="${s.settlement_id === S.sel ? "selected" : ""}">
      <span class="nm">${esc(s.name)}</span>
      <span class="badge"><b>${fmt(s.buildings_le_5m)}</b>≤5 m · #${s.exposure_rank}</span>
      <span class="sub">${esc(s.settlement_id)} · ${esc(s.local_level)} (${s.local_level_type.split(" ")[0]}) · ${esc(s.district)}</span>
    </li>`).join("");
  drawMarkers();
}
$("#list").addEventListener("click", (e) => { const li = e.target.closest("li"); if (li) select(li.dataset.id); });
$("#search").addEventListener("input", debounce(loadList));
["#f-district", "#f-type", "#f-sort"].forEach((q) => $(q).addEventListener("change", loadList));

/* ---------------- selection ---------------- */
async function select(sid) {
  S.sel = sid;
  history.replaceState(null, "", `#${sid}`);
  showView("explorer");
  $$("#list li").forEach((li) => li.classList.toggle("selected", li.dataset.id === sid));
  $(`#list li[data-id="${sid}"]`)?.scrollIntoView({ block: "nearest" });
  const [d, imgs] = await Promise.all([api(`/api/settlements/${sid}`), api(`/api/settlements/${sid}/images`)]);
  S.detail = d; S.images = imgs;
  drawMarkers(); drawWindow(d); drawZones(sid);
  map.flyTo([d.lat, d.lon], 13, { duration: 0.8 });
  $("#detail-empty").hidden = true; $("#detail-body").hidden = false;
  $("#d-title").textContent = `${d.settlement_id} · ${d.name}`;
  $("#d-sub").innerHTML = `${esc(d.local_level)} ${esc(d.local_level_type)}, ${esc(d.district)} District ·
    ${d.nearest_named_water ? `nearest named watercourse ${esc(d.nearest_named_water)} (${fmt(d.nearest_named_water_m)} m)` : "no named watercourse within 3 km"} ·
    point confidence <b>${esc(d.confidence)}</b>${d.selection_method.startsWith("densest") ? " (building-cluster fallback)" : ""}`;
  const sc = Object.fromEntries(d.scenarios.map((x) => [x.level_m, x]));
  $("#d-stats").innerHTML = [
    [fmt(d.buildings_in_window), "buildings in 4×4 km"],
    [fmt(sc[2].buildings), "HAND ≤ 2 m"], [fmt(sc[5].buildings), "HAND ≤ 5 m"], [fmt(sc[10].buildings), "HAND ≤ 10 m"],
    [`#${d.exposure_rank}`, "exposure rank /79"], [`${imgs.length}/12`, "epochs imaged"],
  ].map(([v, l]) => `<div class="stat"><b>${v}</b><span>${l}</span></div>`).join("");
  S.compare.a = imgs[0]?.epoch; S.compare.b = imgs.at(-1)?.epoch;
  renderTab();
}

/* ---------------- tabs ---------------- */
$$(".tabs button").forEach((b) => b.addEventListener("click", () => {
  S.activeTab = b.dataset.tab;
  $$(".tabs button").forEach((x) => x.classList.toggle("active", x === b));
  $$(".tab").forEach((t) => (t.hidden = t.id !== `tab-${S.activeTab}`));
  renderTab();
}));
function renderTab() {
  if (!S.detail) return;
  ({ timeline: renderTimeline, live: renderLive, compare: renderCompare, trends: renderTrends, flood: renderFlood, profile: renderProfile })[S.activeTab]();
}

const imgLabel = (i) => `${i.epoch} · ${i.acquired} · ${i.platform.replace("landsat-", "Landsat ")} ${i.resolution_m} m`;
const frameUrl = (i) => `/${i.frame_path}`;

/* ---- summary card (shared by timeline + compare) ---- */
function summaryHTML(c) {
  const m = c.metrics;
  const row = (label, a, b, dlt, unit = "") => `<tr><td>${label}</td><td>${a}</td><td>${b}</td><td>${dlt}${unit}</td></tr>`;
  const sign = (v, d = 1) => (v === null || v === undefined) ? "–" : `${v > 0 ? "+" : ""}${Number(v).toFixed(d)}`;
  return `<h4>Change ${c.a.acquired} → ${c.b.acquired} <span class="muted small">(${c.years_between} years)</span></h4>
    <ul>${c.summary.map((s) => `<li>${esc(s)}</li>`).join("")}</ul>
    <table><thead><tr><th>Indicator</th><th>${c.a.epoch}</th><th>${c.b.epoch}</th><th>Change</th></tr></thead><tbody>
      ${row("Built-up, window (ha) · GHSL", fmt(m.built_up_ha.a, 1), fmt(m.built_up_ha.b, 1), sign(m.built_up_ha.delta))}
      ${row("Built-up, HAND ≤ 10 m (ha)", fmt(m.built_up_in_hand10_zone_ha.a, 1), fmt(m.built_up_in_hand10_zone_ha.b, 1), sign(m.built_up_in_hand10_zone_ha.delta))}
      ${row("Vegetation cover", pctf(m.vegetation_cover_pct.a), pctf(m.vegetation_cover_pct.b), sign(m.vegetation_cover_pct.delta_pp), " pp")}
      ${row("Surface water", pctf(m.surface_water_pct.a, 2), pctf(m.surface_water_pct.b, 2), sign(m.surface_water_pct.delta_pp, 2), " pp")}
      ${row("Mean NDVI", fmt(m.mean_ndvi.a, 3), fmt(m.mean_ndvi.b, 3), sign(m.mean_ndvi.delta, 3))}
    </tbody></table>
    ${c.cautions.map((x) => `<div class="caution">⚠ ${esc(x)}</div>`).join("")}
    <div class="muted small">${esc(c.evidence)}</div>`;
}

/* ---- timeline ---- */
$("#t-step").addEventListener("change", (e) => { S.timelineStep = +e.target.value; renderTimeline(); });
function chosenEpochs(step) {
  const out = [];
  for (const i of S.images) if (!out.length || i.epoch - out.at(-1).epoch >= step) out.push(i);
  if (S.images.length && out.at(-1) !== S.images.at(-1)) out.push(S.images.at(-1));
  return out;
}
function renderTimeline() {
  const chosen = chosenEpochs(S.timelineStep);
  const byEpoch = Object.fromEntries(S.images.map((i) => [i.epoch, i]));
  const all = S.timelineStep === 5 ? [1972, 1977, 1982, 1987, 1992, 1997, 2002, 2007, 2012, 2017, 2022, 2026] : chosen.map((i) => i.epoch);
  $("#t-strip").innerHTML = all.map((e) => byEpoch[e] && chosen.includes(byEpoch[e])
    ? `<div class="thumb" data-epoch="${e}"><img loading="lazy" src="${frameUrl(byEpoch[e])}" alt="${e}"><div>${e}</div><div class="muted">${byEpoch[e].acquired}</div></div>`
    : `<div class="thumb missing"><div class="ph">${e}<br>no usable image</div></div>`).join("");
  $$("#t-strip .thumb[data-epoch]").forEach((t) => t.addEventListener("click", () => showTimelineEpoch(+t.dataset.epoch)));
  if (chosen.length) showTimelineEpoch(chosen.at(-1).epoch);
}
async function showTimelineEpoch(epoch) {
  const chosen = chosenEpochs(S.timelineStep);
  const idx = chosen.findIndex((i) => i.epoch === epoch);
  const img = chosen[idx];
  $$("#t-strip .thumb").forEach((t) => t.classList.toggle("active", +t.dataset.epoch === epoch));
  $("#t-figure").innerHTML = `<img src="${frameUrl(img)}" alt="${esc(imgLabel(img))}">
    <figcaption>${esc(imgLabel(img))}${img.comparable ? "" : " · false colour (vegetation red)"} · clear ${pctf(img.valid_fraction, 0)}<br>
    Scene <code>${esc(img.scene_id)}</code> · ${esc(img.licence)} · 4×4 km, centre marked on map<br>
    <button id="t-fullres">Full resolution on map</button></figcaption>`;
  $("#t-fullres").addEventListener("click", () => showSceneOnMap(img.collection, img.scene_id, `${img.epoch} ${img.platform}`));
  if (idx <= 0) {
    $("#t-summary").innerHTML = `<h4>${img.epoch}: first image in this series</h4>
      <p class="muted">Select a later image to see the change since the previous one shown, or use the Compare tab for any pair.</p>`;
    return;
  }
  $("#t-summary").innerHTML = `<p class="muted">Computing change…</p>`;
  const c = await api(`/api/compare?settlement_id=${S.sel}&epoch_a=${chosen[idx - 1].epoch}&epoch_b=${epoch}`);
  $("#t-summary").innerHTML = summaryHTML(c);
}

/* ---- compare ---- */
function fillCompareSelects() {
  const opts = S.images.map((i) => `<option value="${i.epoch}">${esc(imgLabel(i))}</option>`).join("");
  $("#c-a").innerHTML = opts; $("#c-b").innerHTML = opts;
  $("#c-a").value = S.compare.a; $("#c-b").value = S.compare.b;
}
$("#c-a").addEventListener("change", (e) => { S.compare.a = +e.target.value; renderCompareView(); });
$("#c-b").addEventListener("change", (e) => { S.compare.b = +e.target.value; renderCompareView(); });
$$(".presets button").forEach((b) => b.addEventListener("click", () => {
  const p = b.dataset.preset;
  if (p === "all") { S.compare.a = S.images[0].epoch; S.compare.b = S.images.at(-1).epoch; }
  else {
    const target = S.compare.b - +p;
    const earlier = S.images.filter((i) => i.epoch <= target);
    S.compare.a = (earlier.at(-1) || S.images[0]).epoch;
  }
  fillCompareSelects(); renderCompareView();
}));
$$(".modes button").forEach((b) => b.addEventListener("click", () => {
  S.compare.mode = b.dataset.mode;
  $$(".modes button").forEach((x) => x.classList.toggle("active", x === b));
  renderCompareView();
}));
function renderCompare() { fillCompareSelects(); renderCompareView(); }
async function renderCompareView() {
  const by = Object.fromEntries(S.images.map((i) => [i.epoch, i]));
  let [a, b] = [by[S.compare.a], by[S.compare.b]];
  if (!a || !b) return;
  if (a.acquired > b.acquired) [a, b] = [b, a];
  const v = $("#c-view");
  if (S.compare.mode === "side") {
    v.innerHTML = `<div class="side">
      <figure><img src="${frameUrl(a)}" alt=""><figcaption>${esc(imgLabel(a))}</figcaption></figure>
      <figure><img src="${frameUrl(b)}" alt=""><figcaption>${esc(imgLabel(b))}</figcaption></figure></div>`;
  } else if (S.compare.mode === "swipe") {
    v.innerHTML = `<div class="swipe"><img src="${frameUrl(b)}" alt=""><div class="top"><img src="${frameUrl(a)}" alt=""></div><div class="line"></div></div>
      <input type="range" min="0" max="100" value="50" aria-label="Swipe position">
      <div class="cap">Left: ${esc(imgLabel(a))} · Right: ${esc(imgLabel(b))}</div>`;
    const wrap = $(".swipe", v), top = $(".top", v), line = $(".line", v), rng = $("input", v);
    const set = () => { const w = wrap.clientWidth; top.style.width = `${rng.value}%`; $("img", top).style.width = `${w}px`; line.style.left = `${rng.value}%`; };
    rng.addEventListener("input", set); $("img", wrap).addEventListener("load", set); set();
  } else {
    v.innerHTML = `<canvas class="diff" width="400" height="400"></canvas>
      <label class="small">Sensitivity <input type="range" min="10" max="120" value="45"></label>
      <div class="cap" id="diff-cap"></div>`;
    drawDiff(a, b, $("canvas", v), $("input", v));
  }
  $("#c-summary").innerHTML = `<p class="muted">Computing change…</p>`;
  const c = await api(`/api/compare?settlement_id=${S.sel}&epoch_a=${a.epoch}&epoch_b=${b.epoch}`);
  $("#c-summary").innerHTML = summaryHTML(c);
}
async function drawDiff(a, b, canvas, slider) {
  const load = (src) => new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = rej; im.src = src; });
  const [ia, ib] = await Promise.all([load(frameUrl(a)), load(frameUrl(b))]);
  const px = (im) => { const c = document.createElement("canvas"); c.width = c.height = 400; const x = c.getContext("2d"); x.drawImage(im, 0, 0, 400, 400); return x.getImageData(0, 0, 400, 400).data; };
  const da = px(ia), db = px(ib), ctx = canvas.getContext("2d");
  const lum = (d, i) => 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
  const render = () => {
    const t = +slider.value, out = ctx.createImageData(400, 400); let n = 0;
    for (let i = 0; i < da.length; i += 4) {
      const g = lum(db, i), dl = g - lum(da, i), big = Math.abs(dl) > t;
      if (big) n++;
      out.data[i] = big ? (dl > 0 ? 235 : 42) : g * 0.6;
      out.data[i + 1] = big ? (dl > 0 ? 104 : 120) : g * 0.6;
      out.data[i + 2] = big ? (dl > 0 ? 52 : 214) : g * 0.6;
      out.data[i + 3] = 255;
    }
    ctx.putImageData(out, 0, 0);
    $("#diff-cap").innerHTML = `<span style="color:#eb6834">■</span> brighter in ${b.epoch} · <span style="color:#2a78d6">■</span> darker in ${b.epoch} ·
      ${(n / (400 * 400) * 100).toFixed(1)}% of pixels flagged. Visual aid only: sensor, season and display differences also create apparent change.`;
  };
  slider.addEventListener("input", render); render();
}

/* ---- trends ---- */
function chartDefaults() {
  Chart.defaults.color = css("--text-secondary");
  Chart.defaults.borderColor = css("--border");
  Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
}
function lineChart(id, labels, datasets, yTitle) {
  S.charts[id]?.destroy();
  S.charts[id] = new Chart($(`#${id}`), {
    type: "line",
    data: { labels, datasets: datasets.map((d, k) => ({ borderWidth: 2, pointRadius: 4, pointHoverRadius: 6, tension: 0,
      borderColor: css(`--series-${k + 1}`), backgroundColor: css(`--series-${k + 1}`), spanGaps: true, ...d })) },
    options: { maintainAspectRatio: false, interaction: { mode: "index", intersect: false },
      plugins: { legend: { display: datasets.length > 1, position: "bottom" } },
      scales: { y: { beginAtZero: true, title: { display: true, text: yTitle } }, x: { grid: { display: false } } } },
  });
}
function renderTrends() {
  chartDefaults();
  const g = S.detail.ghsl;
  lineChart("ch-built", g.map((r) => r.year), [
    { label: "Whole 4×4 km window", data: g.map((r) => r.built_ha_window) },
    { label: "Inside HAND ≤ 10 m zone", data: g.map((r) => r.built_ha_zone10) }], "hectares");
  const cal = S.images.filter((i) => i.comparable);
  lineChart("ch-veg", cal.map((i) => i.acquired.slice(0, 7)), [{ label: "Vegetation cover", data: cal.map((i) => i.veg_fraction * 100) }], "% of clear pixels");
  lineChart("ch-water", cal.map((i) => i.acquired.slice(0, 7)), [{ label: "Surface water", data: cal.map((i) => i.water_fraction * 100) }], "% of clear pixels");
  $("#trend-table").innerHTML = `<div class="table-wrap"><table><thead><tr><th>Epoch</th><th>Acquired</th><th>Sensor</th><th>Clear</th><th>Vegetation</th><th>Water</th><th>Mean NDVI</th></tr></thead><tbody>
    ${S.images.map((i) => `<tr><td>${i.epoch}</td><td>${i.acquired}</td><td>${esc(i.platform)} ${i.resolution_m} m</td><td>${pctf(i.valid_fraction, 0)}</td>
      <td>${i.comparable ? pctf(i.veg_fraction) : "n/c"}</td><td>${i.comparable ? pctf(i.water_fraction, 2) : "n/c"}</td><td>${i.comparable ? fmt(i.ndvi_mean, 3) : "n/c"}</td></tr>`).join("")}
    </tbody></table></div><p class="muted small">n/c = not comparable (uncalibrated 1970s MSS).</p>`;
}

/* ---- flood ---- */
$$("input[data-zone]").forEach((cb) => cb.addEventListener("change", () => {
  const l = layers.zones[cb.dataset.zone]; if (!l) return;
  cb.checked ? l.addTo(map) : map.removeLayer(l);
}));
function renderFlood() {
  const d = S.detail;
  $("#f-table").innerHTML = `<div class="table-wrap"><table><thead><tr><th>Scenario (HAND)</th><th>Buildings in zone</th><th>Share of window buildings</th><th>Zone area in window (ha)</th></tr></thead><tbody>
    ${d.scenarios.map((s) => `<tr><td>≤ ${s.level_m} m above drainage</td><td>${fmt(s.buildings)}</td><td>${pctf(s.share)}</td><td>${fmt(s.zone_area_ha, 1)}</td></tr>`).join("")}
    <tr><td>Buildings within 100 m of a mapped channel</td><td>${fmt(d.buildings_within_100m_of_channel)}</td><td></td><td></td></tr>
    <tr><td>Median building height above drainage</td><td>${fmt(d.median_building_hand_m, 1)} m</td><td></td><td></td></tr>
    </tbody></table></div>
    <p class="muted small">Zones show ground lying within 2, 5 or 10 m of the stream it drains to (Copernicus 30 m DEM, OSM rivers and streams).
      They are not flood extents: there is no discharge, return period, depth, velocity or debris flow.</p>`;
  $("#f-figure").src = `/${d.scenario_figure}`;
}

/* ---- profile ---- */
async function renderProfile() {
  const md = await api(`/api/settlements/${S.sel}/profile`);
  $("#p-body").innerHTML = marked.parse(md.replaceAll("../../outputs/", "/outputs/")) +
    `<p><a href="${REPO}${S.detail.profile_path}" target="_blank" rel="noopener">Open this profile on GitHub</a></p>`;
}


/* ---------------- live monitoring ---------------- */
const catHTML = (mm, cat) => mm === null || mm === undefined ? "–"
  : `${fmt(mm, 1)} mm <span class="cat ${esc(cat || "")}">${/heavy/.test(cat || "") ? "⚠ " : ""}${esc(cat || "")}</span>`;
const ago = (iso) => { if (!iso) return "never"; const m = Math.round((Date.now() - Date.parse(iso)) / 60000);
  return m < 60 ? `${m} min ago` : m < 2880 ? `${Math.round(m / 60)} h ago` : `${Math.round(m / 1440)} days ago`; };

async function renderLive() {
  const d = await api(`/api/live/settlements/${S.sel}`);
  const x = d.summary;
  $("#l-cards").innerHTML = [
    [catHTML(x.rain_past24_mm, x.rain_past24_category), "rain, last 24 h (model)"],
    [catHTML(x.rain_fc_max24_mm, x.rain_fc_max24_category), "max 24 h rain, next 3 days"],
    [x.discharge_fc_ratio === null ? "–" : `${fmt(x.discharge_fc_ratio, 2)}×`, `river forecast max vs 30-day median (${fmt(x.discharge_fc_max, 1)} m³/s)`],
    [x.s1_zone_water_ha === null ? "–" : `${fmt(x.s1_zone_water_ha, 2)} ha`, `radar water in low ground, ${x.s1_latest || "no pass"}${x.s1_water_ratio ? ` (${x.s1_water_ratio}× usual)` : ""}`],
    [x.s2_latest_clear || "–", "latest clear optical image"],
    [fmt(x.incidents_30d), "BIPAD incidents in this local level, 30 days"],
  ].map(([v, l]) => `<div class="stat"><b>${v}</b><em>${l}</em></div>`).join("");

  chartDefaults();
  const rh = d.rain_hourly;
  S.charts["ch-rain"]?.destroy();
  S.charts["ch-rain"] = new Chart($("#ch-rain"), {
    type: "bar",
    data: { labels: rh.map((r) => r.time.slice(5, 13).replace("T", " ")), datasets: [
      { label: "Past (model analysis)", data: rh.map((r) => r.kind === "past" ? r.precip_mm : null), backgroundColor: css("--series-1"), borderRadius: 2 },
      { label: "Forecast", data: rh.map((r) => r.kind === "forecast" ? r.precip_mm : null), backgroundColor: css("--series-2"), borderRadius: 2 }] },
    options: { maintainAspectRatio: false, interaction: { mode: "index", intersect: false }, plugins: { legend: { position: "bottom" } },
      scales: { x: { stacked: true, ticks: { maxTicksLimit: 8 }, grid: { display: false } }, y: { stacked: true, beginAtZero: true, title: { display: true, text: "mm per hour" } } } },
  });
  const q = d.discharge_daily;
  lineChart("ch-q", q.map((r) => r.date.slice(5)), [
    { label: "Past (GloFAS reanalysis/forecast)", data: q.map((r) => r.kind === "past" ? r.discharge : null) },
    { label: "Forecast (ensemble median)", data: q.map((r) => r.kind === "forecast" ? r.discharge_median : null), borderDash: [5, 4] }], "m³/s");
  const cell = q[0];
  $("#l-qnote").textContent = cell ? `GloFAS cell centre ${cell.cell_lat}, ${cell.cell_lon} (~5 km grid): it may represent a larger river than the nearest khola. Model values, not gauge readings.` : "No discharge data yet.";

  $("#l-scenes").innerHTML = d.scenes.length ? d.scenes.map((sc) => `
    <div class="scene">
      ${sc.frame_path ? `<img loading="lazy" src="/live_frames/${sc.frame_path}" alt="">` : `<div class="muted">not processed</div>`}
      <div><b>${sc.acquired}</b> · ${sc.collection === "sentinel-1-rtc" ? "Sentinel-1 radar" : "Sentinel-2 optical"}</div>
      <div class="muted">${sc.collection === "sentinel-1-rtc" ? `water in low ground ${fmt(sc.zone_water_ha, 2)} ha` : `clear ${pctf(sc.clear_fraction, 0)} · water ${fmt(sc.zone_water_ha, 2)} ha`}</div>
      <button data-coll="${sc.collection}" data-item="${esc(sc.scene_id)}" data-label="${sc.acquired}">Full resolution on map</button>
    </div>`).join("") : `<p class="muted">No scenes yet: the satellite job has not run for this settlement.</p>`;
  $$("#l-scenes button").forEach((b) => b.addEventListener("click", () => showSceneOnMap(b.dataset.coll, b.dataset.item, `${b.dataset.label} ${b.dataset.coll}`)));
  $("#l-incidents").innerHTML = incidentTable(d.incidents);
}

function incidentTable(list) {
  if (!list.length) return `<p class="muted">No water-related incidents recorded in BIPAD for this area in the period.</p>`;
  return `<div class="table-wrap"><table><thead><tr><th class="txt">Date</th><th class="txt">Hazard</th><th class="txt">Title</th><th>Deaths</th><th>Missing</th><th>Injured</th><th>Houses destroyed</th><th>Families affected</th></tr></thead><tbody>
    ${list.map((i) => `<tr><td class="txt">${i.incident_on}</td><td class="txt">${esc(i.hazard)}</td>
      <td class="txt"><a href="https://bipadportal.gov.np/incidents/" target="_blank" rel="noopener">${esc(i.title)}</a></td>
      <td>${fmt(i.deaths)}</td><td>${fmt(i.missing)}</td><td>${fmt(i.injured)}</td><td>${fmt(i.houses_destroyed)}</td><td>${fmt(i.families_affected)}</td></tr>`).join("")}
  </tbody></table></div>`;
}

let liveTimer = null;
async function loadLiveView() {
  const [st, ov, inc] = await Promise.all([api("/api/live/status"), api("/api/live/overview"), api("/api/live/incidents?days=30")]);
  if (!st.available) {
    $("#live-status").innerHTML = "No live data yet. Run <code>python dashboard/live_update.py</code> or start the app with <code>LIVE_UPDATES=1</code>.";
  } else {
    $("#live-status").innerHTML = "Last updated: " + Object.entries(st.schedule_minutes).map(([j, m]) =>
      `${j} ${ago(st.last_ok[j])} (every ${m} min)`).join(" · ") + (st.auto_update ? " · auto-update ON" : " · auto-update off (run live_update.py)") +
      (st.recent_errors.length ? ` · <span title="${esc(st.recent_errors[0].message)}">⚠ last error in ${esc(st.recent_errors[0].job)}</span>` : "");
  }
  const heavy = ov.filter((r) => /heavy/.test(r.rain_fc_max24_category || "")).length;
  const rainNow = ov.filter((r) => (r.rain_past24_mm || 0) >= 15.6).length;
  $("#live-cards").innerHTML = [
    [heavy, "settlements with ≥ heavy 24 h rain forecast (next 3 days)"], [rainNow, "with ≥ moderate rain in the last 24 h"],
    [ov.filter((r) => (r.discharge_fc_ratio || 0) >= 2).length, "river forecast ≥ 2× its 30-day median"],
    [ov.filter((r) => (r.s1_water_ratio || 0) >= 1.5).length, "radar low-ground water ≥ 1.5× usual"],
    [inc.length, "water-related incidents reported, 30 days"],
  ].map(([v, l]) => `<div class="card"><b>${v}</b><span>${l}</span></div>`).join("");
  const cols = [["settlement_id", "ID"], ["name", "Settlement"], ["local_level", "Local level"], ["district", "District"],
    ["rain_past24_mm", "Rain 24 h"], ["rain_fc_max24_mm", "Max 24 h forecast"], ["discharge_fc_ratio", "River ratio"],
    ["s1_latest", "Latest radar"], ["s1_water_ratio", "Radar water ratio"], ["s2_latest_clear", "Latest clear optical"], ["incidents_30d", "Incidents 30 d"], ["exposure_rank", "Exposure rank"]];
  let key = "rain_fc_max24_mm", asc = false;
  const cell = (r, k) => k === "rain_past24_mm" ? catHTML(r[k], r.rain_past24_category) : k === "rain_fc_max24_mm" ? catHTML(r[k], r.rain_fc_max24_category)
    : k.endsWith("ratio") ? (r[k] === null ? "–" : `${fmt(r[k], 2)}×`) : typeof r[k] === "number" ? fmt(r[k]) : esc(r[k] ?? "–");
  const draw = () => {
    const sorted = [...ov].sort((a, b) => ((a[key] ?? -1e9) > (b[key] ?? -1e9) ? 1 : -1) * (asc ? 1 : -1));
    $("#live-table").innerHTML = `<table><thead><tr>${cols.map(([k, l]) => `<th data-k="${k}" class="${["settlement_id", "name", "local_level", "district"].includes(k) ? "txt" : ""}">${l}${k === key ? (asc ? " ▲" : " ▼") : ""}</th>`).join("")}</tr></thead>
      <tbody>${sorted.map((r) => `<tr data-id="${r.settlement_id}">${cols.map(([k]) => `<td class="${["settlement_id", "name", "local_level", "district"].includes(k) ? "txt" : ""}">${cell(r, k)}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
    $$("#live-table th").forEach((th) => th.addEventListener("click", () => { asc = key === th.dataset.k ? !asc : false; key = th.dataset.k; draw(); }));
    $$("#live-table tbody tr").forEach((tr) => tr.addEventListener("click", () => { S.activeTab = "live"; activateTab("live"); select(tr.dataset.id); }));
  };
  draw();
  $("#live-incidents").innerHTML = incidentTable(inc).replace(/^<div class="table-wrap">|<\/div>$/g, "");
  clearTimeout(liveTimer);
  liveTimer = setTimeout(() => { if (!$("#view-live").hidden) loadLiveView(); }, 5 * 60 * 1000);
}

function activateTab(name) {
  $$(".tabs button").forEach((x) => x.classList.toggle("active", x.dataset.tab === name));
  $$(".tab").forEach((t) => (t.hidden = t.id !== `tab-${name}`));
}

/* ---------------- views ---------------- */
$$(".views button").forEach((b) => b.addEventListener("click", () => showView(b.dataset.view)));
function showView(v) {
  $$(".views button").forEach((x) => x.classList.toggle("active", x.dataset.view === v));
  $$(".view").forEach((x) => (x.hidden = x.id !== `view-${v}`));
  if (v === "explorer") setTimeout(() => map.invalidateSize(), 50);
  if (v === "province" && !S.provinceLoaded) loadProvince();
  if (v === "live") loadLiveView();
  if (v === "about") renderAbout();
}

async function loadProvince() {
  S.provinceLoaded = true; chartDefaults();
  const [p, all] = await Promise.all([api("/api/province"), api("/api/settlements?sort=rank")]);
  const tot = (k) => all.reduce((s, r) => s + r[k], 0);
  const imgs = p.image_coverage.reduce((s, r) => s + r.images, 0);
  $("#prov-cards").innerHTML = [
    ["79", "local-level settlements (25 urban, 54 rural)"], [fmt(tot("buildings_in_window")), "buildings in analysis windows"],
    [fmt(tot("buildings_le_2m")), "on ground HAND ≤ 2 m"], [fmt(tot("buildings_le_5m")), "HAND ≤ 5 m"],
    [fmt(tot("buildings_le_10m")), "HAND ≤ 10 m"], [fmt(imgs), "satellite frames, 1972–2026"],
  ].map(([v, l]) => `<div class="card"><b>${v}</b><span>${l}</span></div>`).join("");
  S.charts.district?.destroy();
  S.charts.district = new Chart($("#ch-district"), {
    type: "bar",
    data: { labels: p.by_district.map((r) => r.district), datasets: [{ label: "Buildings HAND ≤ 5 m", data: p.by_district.map((r) => r.le5),
      backgroundColor: css("--series-1"), borderRadius: 4, borderSkipped: "start", maxBarThickness: 22 }] },
    options: { indexAxis: "y", maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { display: false } } } },
  });
  lineChart("ch-prov-built", p.ghsl.map((r) => r.year), [
    { label: "All 79 windows", data: p.ghsl.map((r) => r.built_ha_window) },
    { label: "Inside HAND ≤ 10 m zones", data: p.ghsl.map((r) => r.built_ha_zone10) }], "hectares");
  const cols = [["settlement_id", "ID"], ["name", "Settlement"], ["local_level", "Local level"], ["local_level_type", "Type"], ["district", "District"],
    ["buildings_in_window", "Buildings"], ["buildings_le_2m", "≤ 2 m"], ["buildings_le_5m", "≤ 5 m"], ["buildings_le_10m", "≤ 10 m"], ["share_le_5m", "Share ≤ 5 m"], ["exposure_rank", "Rank"]];
  let sortKey = "exposure_rank", asc = true;
  const draw = () => {
    const r = [...all].sort((x, y) => (x[sortKey] > y[sortKey] ? 1 : -1) * (asc ? 1 : -1));
    $("#prov-table").innerHTML = `<table><thead><tr>${cols.map(([k, l]) => `<th data-k="${k}" class="${typeof all[0][k] === "number" ? "" : "txt"}">${l}${k === sortKey ? (asc ? " ▲" : " ▼") : ""}</th>`).join("")}</tr></thead>
      <tbody>${r.map((s) => `<tr data-id="${s.settlement_id}">${cols.map(([k]) => `<td class="${typeof s[k] === "number" ? "" : "txt"}">${k === "share_le_5m" ? pctf(s[k]) : k === "local_level_type" ? s[k].split(" ")[0] : typeof s[k] === "number" ? fmt(s[k]) : esc(s[k])}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
    $$("#prov-table th").forEach((th) => th.addEventListener("click", () => { asc = sortKey === th.dataset.k ? !asc : true; sortKey = th.dataset.k; draw(); }));
    $$("#prov-table tbody tr").forEach((tr) => tr.addEventListener("click", () => select(tr.dataset.id)));
  };
  draw();
}

function renderAbout() {
  $("#about-body").innerHTML = marked.parse(`
## What this portal shows

For the primary settlement of each of Karnali Province's **79 local levels** (25 urban, 54 rural municipalities):

- **Timeline:** one satellite image per 5-year epoch from the first Landsat acquisition (1972) to the 2026 dry season. You can view it every 5 or 10 years.
- **Compare:** any two epochs side by side, as a swipe, or as a brightness-difference view, with a computed change summary.
- **Trends:** GHSL built-up surface 1975–2020 (whole window and on low ground), plus vegetation and surface-water indicators from calibrated images.
- **Low-ground scenarios:** ground within 2, 5 and 10 m of the drainage it flows to (HAND), with building counts. Zones can be shown on the map.

## How to read it

| Category | Examples here |
|---|---|
| Observed | satellite images |
| Derived | built-up area, vegetation and water shares, HAND zones, building counts |
| Not provided | flood probability, depth or velocity, population, vulnerability, **risk to life** |

Apparent change between images can come from sensor, resolution, season, sun angle, snow or cloud. Each comparison lists these cautions.

## Data sources

COD-AB Nepal boundaries (Survey Dept. of Nepal / OCHA, CC BY-IGO) · Overture Maps 2026-09-23.1: places, rivers, buildings (OSM ODbL, Google Open Buildings CC BY 4.0, Microsoft ODbL) ·
Copernicus DEM GLO-30 · Landsat Collection 2 (USGS, public domain) · Sentinel-2 L2A (Copernicus) · JRC GHS-BUILT-S R2023A (CC BY 4.0).

## Documentation

- [Methodology](${REPO}docs/methodology.md) · [Limitations](${REPO}docs/limitations.md) · [Data sources](${REPO}docs/data_sources.md)
- [Screening report](${REPO}outputs/reports/karnali_79_exposure_screening_report.md) · [Dashboard README](${REPO}dashboard/README.md)
`);
}

/* ---------------- boot ---------------- */
(async function boot() {
  const meta = await api("/api/meta");
  $("#f-district").innerHTML += meta.districts.map((d) => `<option>${esc(d)}</option>`).join("");
  const lv = await api("/api/local_levels");
  layers.levels.addData(lv).setStyle((f) => ({ color: css("--text-muted"), weight: 0.6,
    fillColor: css("--series-2"), fillOpacity: f.properties.local_level_type.startsWith("urban") ? 0.08 : 0 }));
  layers.levels.eachLayer((l) => l.bindTooltip(`${esc(l.feature.properties.name)} (${esc(l.feature.properties.local_level_type)})`, { sticky: true }));
  layers.levels.addTo(map);
  initGibs();
  map.fitBounds(layers.levels.getBounds(), { padding: [10, 10] });
  await loadList();
  const fromHash = () => {
    const h = location.hash.slice(1);
    if (h && h !== S.sel && S.list.some((s) => s.settlement_id === h)) select(h);
  };
  window.addEventListener("hashchange", fromHash);
  fromHash();
})();
