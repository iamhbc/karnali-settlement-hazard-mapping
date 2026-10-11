import unittest
import sys
import tempfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analysis.hazard_exposure.validate_karnali_79 import _raster_check, validate


class KarnaliOutputValidationTests(unittest.TestCase):
    def test_committed_outputs_are_structurally_consistent(self):
        errors, _, summary = validate(ROOT)

        self.assertFalse(errors, "\n".join(errors))
        self.assertEqual(summary["settlements"], 79)
        self.assertEqual(summary["settlement_geometries"], 79)
        self.assertEqual(summary["local_levels"], 79)
        self.assertEqual(summary["water_level_zones"], 79 * 3)

    def test_raster_check_detects_misaligned_grids(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / "ghsl"
            folder.mkdir()
            for year, x_origin in ((1975, 0), (1980, 1)):
                path = folder / f"karnali_built_s_E{year}.tif"
                profile = {
                    "driver": "GTiff",
                    "height": 2,
                    "width": 2,
                    "count": 1,
                    "dtype": "uint8",
                    "crs": "EPSG:4326",
                    "transform": from_origin(x_origin, 2, 1, 1),
                }
                with rasterio.open(path, "w", **profile) as raster:
                    raster.write(np.zeros((2, 2), dtype=np.uint8), 1)

            errors, warnings = [], []
            checked = _raster_check(Path(temp), [1975, 1980], errors, warnings)

        self.assertEqual(checked, 2)
        self.assertTrue(any("grid for 1980 differs" in error for error in errors))
