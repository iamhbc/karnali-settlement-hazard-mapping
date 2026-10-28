"""Per-epoch image frames and spectral indicators for the dashboard.

Re-reads exactly the scenes recorded in data/metadata/imagery_catalog.csv (no re-selection),
writes one display JPEG per settlement-epoch on a common pixel grid, and measures simple
spectral indicators over the chip:

  ndvi_mean        mean NDVI of valid pixels
  veg_fraction     share of valid pixels with NDVI > 0.3
  water_fraction   share of valid pixels with MNDWI > 0 (green/SWIR1); MSS: NDWI > 0 (green/NIR)
  brightness_mean  mean visible reflectance (MSS: not computed, DN only)
  valid_fraction   share of chip pixels that are neither no-data nor cloud/shadow/snow

Landsat L2 and Sentinel-2 indicators are computed on surface reflectance and are broadly
comparable across dates (sensor differences remain). 1970s MSS indicators are computed on
uncalibrated DN and are flagged ``comparable=False``: they are shown but must not be
differenced against later sensors.
"""
from __future__ import annotations

import numpy as np
import planetary_computer as pc
from PIL import Image
from rasterio.enums import Resampling

from remote_sensing.imagery_timeseries import bad_mask, read_band, stretch, to_reflectance

BANDS = {
    "landsat-c2-l1": dict(red="red", green="green", nir="nir08", swir=None, qa="qa_pixel", res=60,
                          rgb=["nir08", "red", "green"]),
    "landsat-c2-l2": dict(red="red", green="green", nir="nir08", swir="swir16", qa="qa_pixel", res=30,
                          rgb=["red", "green", "blue"]),
    "sentinel-2-l2a": dict(red="B04", green="B03", nir="B08", swir="B11", qa="SCL", res=10,
                           rgb=["B04", "B03", "B02"]),
}


class _Chip:  # minimal stand-in so stretch() applies the same display rules as the figures
    def __init__(self, rgb, collection):
        self.rgb, self.collection = rgb, collection


def frame_and_indicators(catalog, collection: str, item_id: str, bounds, crs: str, out_path,
                         size_px: int = 400) -> dict:
    spec = BANDS[collection]
    item = next(catalog.search(collections=[collection], ids=[item_id]).items())
    item = pc.sign(item)
    date = item.datetime.date()

    def band(name, resampling=Resampling.bilinear):
        return read_band(item.assets[name].href, bounds, crs, spec["res"], resampling)

    qa = band(spec["qa"], Resampling.nearest)
    obscured, nodata = bad_mask(collection, qa)
    valid = ~(obscured | nodata)

    rgb = np.stack([band(b).astype(np.float32) for b in spec["rgb"]])
    rgb = to_reflectance(collection, rgb, date)
    img = (stretch(_Chip(rgb, collection)) * 255).astype(np.uint8)
    Image.fromarray(img).resize((size_px, size_px), Image.NEAREST).save(out_path, quality=88)

    def refl(name):
        return to_reflectance(collection, band(name).astype(np.float32)[None], date)[0]

    red, green, nir = refl(spec["red"]), refl(spec["green"]), refl(spec["nir"])
    with np.errstate(invalid="ignore", divide="ignore"):
        ndvi = (nir - red) / (nir + red)
        if spec["swir"]:
            swir = refl(spec["swir"])
            water = (green - swir) / (green + swir)
        else:
            water = (green - nir) / (green + nir)
    v = valid & np.isfinite(ndvi) & np.isfinite(water)
    n = max(int(v.sum()), 1)
    comparable = collection != "landsat-c2-l1"
    return dict(
        acquired=date.isoformat(),
        valid_fraction=round(float(v.mean()), 4),
        ndvi_mean=round(float(np.nanmean(ndvi[v])), 4) if v.any() else None,
        veg_fraction=round(float((ndvi[v] > 0.3).sum() / n), 4) if v.any() else None,
        water_fraction=round(float((water[v] > 0).sum() / n), 4) if v.any() else None,
        brightness_mean=(round(float(np.nanmean(((red + green) / 2)[v])), 4)
                         if comparable and v.any() else None),
        comparable=comparable,
        resolution_m=spec["res"],
    )

