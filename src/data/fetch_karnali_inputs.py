"""Fetch the open input datasets for the Karnali 79-settlement screening into a local cache.

Nothing here is committed to the repository: the cache ($KARNALI_CACHE) is disposable and
every source, version and licence is recorded in data/metadata/datasets.csv.

  admin      OCHA/HDX COD-AB Nepal (Survey Department of Nepal), CC BY-IGO -> 79 Karnali adm3 units
  overture   Overture Maps release (configs: karnali_79_screening.overture_release), via DuckDB:
             divisions/locality (OSM-derived, ODbL), base/water (OSM, ODbL),
             buildings (OSM ODbL + Google Open Buildings CC BY 4.0 + Microsoft ML Buildings ODbL)
  ghsl       JRC GHS-BUILT-S R2023A, 3 arcsec, epochs 1975-2020 (+2025 model), CC BY 4.0

Usage:  KARNALI_CACHE=/path python src/data/fetch_karnali_inputs.py [admin|overture|ghsl ...]
"""
from __future__ import annotations

import os
import subprocess
import sys
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

import yaml

ROOT = Path(__file__).resolve().parents[2]
CACHE = Path(os.environ.get("KARNALI_CACHE", "/tmp/karnali_cache"))
CFG = yaml.safe_load(open(ROOT / "configs/analysis_parameters.yaml"))["karnali_79_screening"]

COD_AB_GDB = ("https://data.humdata.org/dataset/07db728a-4f0f-4e98-8eb0-8fa9df61f01c/resource/"
              "37775d96-2b6a-47b4-8465-2b3238368567/download/npl_admin_boundaries.gdb.zip")
GHSL = ("https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_BUILT_S_GLOBE_R2023A/"
        "GHS_BUILT_S_E{y}_GLOBE_R2023A_4326_3ss/V1-0/tiles/GHS_BUILT_S_E{y}_GLOBE_R2023A_4326_3ss_V1_0_{t}.zip")
GHSL_TILES = ["R6_C27", "R7_C27"]          # 10x10 degree tiles covering Karnali
BBOX_PAD = (80.95, 28.10, 83.75, 30.50)    # crop window (lon/lat) slightly larger than the province


def download(url: str, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers={"User-Agent": "karnali-settlement-hazard-mapping research"})
    with urlopen(req, timeout=600) as r, open(dest, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)


def fetch_admin():
    import geopandas as gpd
    z = CACHE / "admin/npl_admin_boundaries.gdb.zip"
    download(COD_AB_GDB, z)
    zipfile.ZipFile(z).extractall(CACHE / "admin")
    adm3 = gpd.read_file(CACHE / "admin/npl_admin_boundaries.gdb", layer="npl_admin3")
    k = adm3[adm3["adm1_name"] == "Karnali"]
    assert len(k) == 79, f"expected 79 Karnali local levels, got {len(k)}"
    k.to_parquet(CACHE / "admin/karnali_adm3.parquet")
    z.unlink()


def fetch_overture():
    import duckdb
    import geopandas as gpd
    x0, y0, x1, y1 = gpd.read_parquet(CACHE / "admin/karnali_adm3.parquet").total_bounds
    rel = f"s3://overturemaps-us-west-2/release/{CFG['overture_release']}"
    bb = f"bbox.xmin>{x0} AND bbox.xmax<{x1} AND bbox.ymin>{y0} AND bbox.ymax<{y1}"
    con = duckdb.connect()
    con.sql("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs; SET s3_region='us-west-2';")
    con.sql(f"""COPY (SELECT id, names.primary AS name, names.common['en'] AS name_en, subtype, class,
                population, sources[1].dataset AS src, sources[1].record_id AS src_id, geometry
        FROM read_parquet('{rel}/theme=divisions/type=division/*') WHERE {bb} AND subtype='locality')
        TO '{CACHE}/overture_localities.parquet' (FORMAT parquet)""")
    con.sql(f"""COPY (SELECT id, names.primary AS name, subtype, class, sources[1].dataset AS src, geometry
        FROM read_parquet('{rel}/theme=base/type=water/*') WHERE {bb}
        AND subtype IN ('river','stream','canal','water','lake','reservoir'))
        TO '{CACHE}/overture_water.parquet' (FORMAT parquet)""")
    con.sql(f"""COPY (SELECT id, sources[1].dataset AS src,
                ST_Area_Spheroid(ST_FlipCoordinates(geometry)) AS area_m2,
                ST_X(ST_Centroid(geometry)) lon, ST_Y(ST_Centroid(geometry)) lat
        FROM read_parquet('{rel}/theme=buildings/type=building/*') WHERE {bb})
        TO '{CACHE}/overture_buildings.parquet' (FORMAT parquet)""")


def fetch_ghsl():
    out = CACHE / "ghsl"
    for y in CFG["ghsl_epochs"]:
        tifs = []
        for t in GHSL_TILES:
            z = out / f"E{y}_{t}.zip"
            download(GHSL.format(y=y, t=t), z)
            with zipfile.ZipFile(z) as zf:
                name = next(n for n in zf.namelist() if n.endswith(".tif"))
                zf.extract(name, out)
                tifs.append(str(out / name))
            z.unlink()
        vrt = out / f"E{y}.vrt"
        subprocess.run(["gdalbuildvrt", "-q", str(vrt), *tifs], check=True)
        subprocess.run(["gdal_translate", "-q", "-projwin", str(BBOX_PAD[0]), str(BBOX_PAD[3]),
                        str(BBOX_PAD[2]), str(BBOX_PAD[1]), "-co", "COMPRESS=DEFLATE", str(vrt),
                        str(out / f"karnali_built_s_E{y}.tif")], check=True)
        for f in tifs + [str(vrt)]:
            Path(f).unlink()


if __name__ == "__main__":
    steps = sys.argv[1:] or ["admin", "overture", "ghsl"]
    for s in steps:
        print("fetching", s, flush=True)
        {"admin": fetch_admin, "overture": fetch_overture, "ghsl": fetch_ghsl}[s]()
