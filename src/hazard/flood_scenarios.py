"""Terrain-based water-level scenarios using Height Above Nearest Drainage (HAND).

Method (documented in docs/methodology.md):
  1. Read Copernicus GLO-30 DEM on the analysis grid.
  2. Rasterize mapped channels (Overture/OSM river and stream lines and river polygons).
  3. Burn channels into the DEM, condition it (fill pits/depressions, resolve flats) and
     derive D8 flow directions (pysheds).
  4. HAND of every cell = its (unconditioned) DEM elevation minus the elevation of the
     channel cell its D8 flow path drains into (Nobre et al. 2011, J. Hydrol. 404:13-29).
     Cells whose path leaves the context window before reaching a channel are NaN.
  5. Scenario zone for water level h = cells with HAND <= h.

This is an exposure SCREENING of which ground lies within h metres above the drainage it
flows to. It is NOT a hydraulic/hydrodynamic flood model: it has no discharge, return
period, flow velocity, timing, debris, or defence information, and DEM vertical error
(several metres in steep terrain) is of the same order as h.
"""
from __future__ import annotations

import numpy as np
import planetary_computer as pc
import pystac_client
from rasterio.enums import Resampling
from rasterio.features import rasterize
from scipy import ndimage

from remote_sensing.imagery_timeseries import STAC_URL, read_band


def read_dem(bounds, crs: str, res: float) -> np.ndarray:
    """Copernicus GLO-30 DEM warped to the analysis grid (may span several 1-degree tiles)."""
    from shapely.geometry import box
    import pyproj
    from shapely.ops import transform as shp_transform

    to_ll = pyproj.Transformer.from_crs(crs, 4326, always_xy=True).transform
    aoi = shp_transform(to_ll, box(*bounds))
    cat = pystac_client.Client.open(STAC_URL)
    items = list(cat.search(collections=["cop-dem-glo-30"], intersects=aoi.__geo_interface__).items())
    if not items:
        raise RuntimeError("No Copernicus DEM tile found for the analysis area")
    dem = None
    for it in items:
        arr = read_band(pc.sign(it).assets["data"].href, bounds, crs, res, Resampling.bilinear)
        arr = np.where(arr == 0, np.nan, arr.astype(np.float32))
        dem = arr if dem is None else np.where(np.isnan(dem), arr, dem)
    return dem, [it.id for it in items]


def channel_mask(lines, polygons, transform, shape) -> np.ndarray:
    shapes = [(g, 1) for g in list(lines) + list(polygons) if g is not None and not g.is_empty]
    if not shapes:
        return np.zeros(shape, dtype=bool)
    return rasterize(shapes, out_shape=shape, transform=transform, all_touched=True,
                     fill=0, dtype="uint8").astype(bool)


def hand(dem: np.ndarray, channels: np.ndarray, transform, crs: str, burn_m: float):
    """HAND (m) and Euclidean distance to the nearest channel cell (cells)."""
    if not hasattr(np, "in1d"):  # pysheds 0.5 still calls the removed numpy alias
        np.in1d = np.isin
    import pyproj
    from pysheds.grid import Grid
    from pysheds.sview import Raster, ViewFinder

    filled = np.where(np.isnan(dem), np.nanmin(dem), dem).astype(np.float64)
    vf = ViewFinder(affine=transform, shape=dem.shape, crs=pyproj.Proj(crs), nodata=np.nan)
    grid = Grid(viewfinder=vf)
    burned = Raster(np.where(channels, filled - burn_m, filled), viewfinder=vf)
    cond = grid.resolve_flats(grid.fill_depressions(grid.fill_pits(burned)))
    fdir = grid.flowdir(cond)
    mask = Raster(channels, viewfinder=ViewFinder(affine=transform, shape=dem.shape,
                                                  crs=pyproj.Proj(crs), nodata=False))
    h = np.asarray(grid.compute_hand(fdir, Raster(filled, viewfinder=vf), mask), dtype=float)
    h[np.isnan(dem)] = np.nan
    dist = ndimage.distance_transform_edt(~channels)
    return h, dist


def scenario_zone(hand_m: np.ndarray, h: float) -> np.ndarray:
    return np.nan_to_num(hand_m, nan=np.inf) <= h
