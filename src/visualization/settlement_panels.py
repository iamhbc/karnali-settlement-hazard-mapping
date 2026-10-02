"""Figures for the Karnali 79-settlement screening: image time series and water-level scenarios."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402

# Devanagari fallback for settlement names without an English form (macOS system font).
plt.rcParams["font.family"] = ["DejaVu Sans", "Kohinoor Devanagari"]

from remote_sensing.imagery_timeseries import stretch  # noqa: E402

SCENARIO_COLOURS = {2: "#08306b", 5: "#2171b5", 10: "#6baed6"}


def _scalebar(ax, extent_m: float, n_px: int, km: float = 1.0):
    px = n_px * km * 1000 / extent_m
    ax.plot([n_px * 0.06, n_px * 0.06 + px], [n_px * 0.93] * 2, color="white", lw=3)
    ax.text(n_px * 0.06 + px / 2, n_px * 0.89, f"{km:g} km", color="white", ha="center",
            fontsize=7, weight="bold")


def timeseries_figure(path, title: str, subtitle: str, chips: list, extent_m: float):
    n = len(chips)
    cols = 4
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3.2, rows * 3.75 + 0.9))
    for ax in axes.ravel():
        ax.axis("off")
    for ax, (label, chip) in zip(axes.ravel(), chips):
        if chip is None:
            ax.text(0.5, 0.5, f"{label}\nno usable dry-season scene\nin the archive window\n(missing or cloudy)", ha="center",
                    va="center", fontsize=9, transform=ax.transAxes, color="#555")
            continue
        img = stretch(chip)
        h, w = img.shape[:2]
        ax.imshow(img, interpolation="nearest")
        ax.plot(w / 2, h / 2, marker="+", color="yellow", ms=10, mew=1.5)
        _scalebar(ax, extent_m, w)
        sensor = chip.platform.replace("landsat-", "Landsat ").replace("Sentinel-", "S")
        ax.set_title(f"{label}: {chip.acquired}\n{sensor}, {chip.resolution_m} m"
                     + (" (false colour)" if "false" in chip.display else ""), fontsize=8)
    fig.suptitle(title, fontsize=12, weight="bold", y=0.995)
    fig.text(0.5, 0.955, subtitle, ha="center", fontsize=8, color="#333")
    fig.text(0.01, 0.005, "Imagery: Landsat (USGS, public domain) and Copernicus Sentinel-2 (ESA), "
             "via Microsoft Planetary Computer. Landsat L2/Sentinel-2: surface reflectance on one fixed "
             "display scale; 1970s MSS: per-image stretch, false colour. + = selected settlement point.",
             fontsize=6.5, color="#444")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.03, wspace=0.05, hspace=0.28)
    fig.savefig(path, dpi=110)
    plt.close(fig)


def scenario_figure(path, title: str, base_chip, zones: dict, buildings_px: np.ndarray,
                    in_zone: dict, rem: np.ndarray, ghsl: dict, ghsl_zone: dict, levels):
    fig = plt.figure(figsize=(14, 5.2))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.15])
    ax0 = fig.add_subplot(gs[0])
    ax1 = fig.add_subplot(gs[1])
    ax2 = fig.add_subplot(gs[2])
    shape = rem.shape
    if base_chip is not None:
        ax0.imshow(stretch(base_chip), extent=(0, shape[1], shape[0], 0))
        ax0.set_title(f"Water-level scenarios on {base_chip.platform} {base_chip.acquired}", fontsize=9)
    for h in sorted(levels, reverse=True):
        cmap = ListedColormap(["none", SCENARIO_COLOURS[h]])
        ax0.imshow(zones[h].astype(int), cmap=cmap, alpha=0.55, interpolation="nearest",
                   extent=(0, shape[1], shape[0], 0))
    if len(buildings_px):
        hit = in_zone[max(levels)]
        ax0.scatter(buildings_px[~hit, 0], buildings_px[~hit, 1], s=1, c="#ffd54f", lw=0)
        ax0.scatter(buildings_px[hit, 0], buildings_px[hit, 1], s=2, c="#d7191c", lw=0)
    handles = [plt.Rectangle((0, 0), 1, 1, color=SCENARIO_COLOURS[h], alpha=0.7) for h in levels]
    ax0.legend(handles, [f"HAND <= {h} m" for h in levels], fontsize=7, loc="lower right")
    ax0.axis("off")

    im = ax1.imshow(np.clip(rem, -5, 60), cmap="terrain")
    ax1.set_title("Height above nearest drainage, HAND (m, Copernicus GLO-30)\n"
                  "white = 60 m or more / drains outside window", fontsize=9)
    ax1.axis("off")
    fig.colorbar(im, ax=ax1, fraction=0.046, pad=0.02)

    yrs = sorted(ghsl)
    ax2.plot(yrs, [ghsl[y] / 1e4 for y in yrs], "-o", ms=3, label="whole 4x4 km window", color="#444")
    ax2.plot(yrs, [ghsl_zone[y] / 1e4 for y in yrs], "-o", ms=3, color="#d7191c",
             label=f"inside <= {max(levels)} m scenario zone")
    ax2.set_ylabel("Built-up surface (ha), GHSL R2023A")
    ax2.set_title("Built-up surface 1975-2020 (5-year epochs, 100 m grid)", fontsize=9)
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=7)
    counts = ", ".join(f"<= {h} m: {int(in_zone[h].sum())}" for h in levels)
    fig.suptitle(f"{title}\nBuildings in scenario zones ({counts}; total {len(buildings_px)})",
                 fontsize=10, weight="bold")
    fig.text(0.01, 0.01, "SCREENING ONLY: terrain-based HAND zones, not a hydraulic flood "
             "model (no discharge, return period, velocity or debris flow). DEM vertical error is "
             "several metres in steep terrain. Buildings: Overture Maps (OSM, Google, Microsoft).",
             fontsize=6.5, color="#444")
    fig.subplots_adjust(left=0.01, right=0.98, top=0.82, bottom=0.1, wspace=0.32)
    fig.savefig(path, dpi=110)
    plt.close(fig)
