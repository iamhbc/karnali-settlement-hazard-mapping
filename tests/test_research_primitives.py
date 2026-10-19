import datetime as dt

import numpy as np

from hazard.flood_scenarios import scenario_zone
from remote_sensing.imagery_timeseries import bad_mask, to_reflectance


def test_landsat_bad_mask_distinguishes_obscuration_and_nodata():
    qa = np.array([0, 1, 2, 8, 16, 32, 4], dtype=np.uint16)

    obscured, nodata = bad_mask("landsat-c2-l2", qa)

    np.testing.assert_array_equal(obscured, [False, False, True, True, True, True, False])
    np.testing.assert_array_equal(nodata, [True, True, False, False, False, False, False])


def test_sentinel_bad_mask_marks_cloud_classes_but_not_clear_or_nodata():
    qa = np.array([0, 3, 8, 9, 10, 11, 4], dtype=np.uint8)

    obscured, nodata = bad_mask("sentinel-2-l2a", qa)

    np.testing.assert_array_equal(obscured, [False, True, True, True, True, True, False])
    np.testing.assert_array_equal(nodata, [True, False, False, False, False, False, False])


def test_sentinel_reflectance_applies_processing_baseline_offset_by_date():
    dn = np.array([2000], dtype=np.uint16)

    before_offset = to_reflectance("sentinel-2-l2a", dn.copy(), dt.date(2022, 1, 24))
    after_offset = to_reflectance("sentinel-2-l2a", dn.copy(), dt.date(2022, 1, 25))

    np.testing.assert_allclose(before_offset, [0.2])
    np.testing.assert_allclose(after_offset, [0.1])


def test_scenario_zone_excludes_missing_hand_values():
    hand_m = np.array([[0.0, 2.0, 5.01], [np.nan, 10.0, -1.0]])

    zone = scenario_zone(hand_m, 5.0)

    np.testing.assert_array_equal(zone, [[True, True, False], [False, False, True]])
