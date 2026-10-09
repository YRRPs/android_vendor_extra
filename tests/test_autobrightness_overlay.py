#
# SPDX-FileCopyrightText: Yim's Riced ROM Project
# SPDX-License-Identifier: Apache-2.0
#
"""Checks the salami indoor auto-brightness overlay against upstream."""

import itertools
import math
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "autobrightness"))

import gen_overlay

# Issue #24: the first 24 upstream points stretched with D = 5.
EXPECTED_STRETCHED_D5 = [
    5, 20, 60, 100, 140, 235, 315, 430, 750, 1100, 1350, 1800, 2100, 2550,
    3100, 5000, 6160, 7029, 7583, 8126, 8673, 9225, 9778, 11146,
]


class StretchLevelsTest(unittest.TestCase):
    def test_stretches_issue_points_with_divisor_five(self):
        upstream = [1, 4, 12, 20, 28, 47, 63, 86, 150, 220, 270, 360, 420,
                    510, 620, 1000, 2000, 3100, 3988, 5018, 6232, 7648,
                    9280, 11146]
        self.assertEqual(gen_overlay.stretch_levels(upstream, 5),
                         EXPECTED_STRETCHED_D5)

    def test_rejects_divisor_of_ten_or_more(self):
        # At or above D = 10 the taper shrinks points faster than lux grows.
        for divisor in (10, 20):
            with self.assertRaises(ValueError):
                gen_overlay.stretch_levels([1, 2], divisor)

    def test_rejects_non_finite_divisor(self):
        for divisor in (math.nan, math.inf):
            with self.assertRaises(ValueError):
                gen_overlay.stretch_levels([1, 2], divisor)

    def test_accepts_divisor_just_below_ten(self):
        self.assertEqual(gen_overlay.stretch_levels([9280, 11146], 9.9)[-1],
                         11146)

    def test_rejects_divisor_below_one(self):
        with self.assertRaises(ValueError):
            gen_overlay.stretch_levels([1, 2], 0.5)


class UpstreamCurveTest(unittest.TestCase):
    def test_reads_both_arrays_from_snapshot(self):
        curve = gen_overlay.read_curve(gen_overlay.UPSTREAM_SNAPSHOT)
        self.assertEqual(curve.levels[:3], [1, 4, 12])
        self.assertEqual(curve.nits[:2], ["2.0487", "4.8394"])
        self.assertEqual(len(curve.levels) + 1, len(curve.nits))


class CommittedOverlayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.upstream = gen_overlay.read_curve(gen_overlay.UPSTREAM_SNAPSHOT)
        cls.overlay = gen_overlay.read_curve(gen_overlay.OVERLAY_CONFIG)

    def test_has_one_fewer_lux_point_than_nits(self):
        self.assertEqual(len(self.overlay.levels) + 1, len(self.overlay.nits))

    def test_lux_points_strictly_increase(self):
        pairs = itertools.pairwise(self.overlay.levels)
        self.assertTrue(all(a < b for a, b in pairs), self.overlay.levels)

    def test_daylight_points_match_upstream(self):
        for index, lux in enumerate(self.upstream.levels):
            if lux >= gen_overlay.TAPER_END_LUX:
                self.assertEqual(self.overlay.levels[index], lux)

    def test_first_point_stays_above_framework_zero_point(self):
        # The framework prepends a 0 lux point to the levels array.
        self.assertGreater(self.overlay.levels[0], 0)

    def test_nits_copy_upstream_unchanged(self):
        self.assertEqual(self.overlay.nits, self.upstream.nits)

    def test_committed_file_matches_generator(self):
        actual = gen_overlay.OVERLAY_CONFIG.read_text(encoding="utf-8")
        divisor = gen_overlay.read_divisor(actual)
        expected = gen_overlay.render(self.upstream, divisor)
        self.assertEqual(actual, expected,
                         "rerun tools/autobrightness/gen_overlay.py")


class PackagingTest(unittest.TestCase):
    MODULE = "YrrpSalamiAutoBrightness"
    UPSTREAM_PRIORITY = 350  # android.overlay.oplus.target
    ANDROID_NS = "{http://schemas.android.com/apk/res/android}"

    def test_manifest_is_static_android_overlay_above_device_overlay(self):
        manifest = ROOT / "overlay" / self.MODULE / "AndroidManifest.xml"
        overlay = ET.parse(manifest).getroot().find("overlay")
        attr = {key.replace(self.ANDROID_NS, ""): value
                for key, value in overlay.attrib.items()}
        self.assertEqual(attr["targetPackage"], "android")
        self.assertEqual(attr["isStatic"], "true")
        self.assertGreater(int(attr["priority"]), self.UPSTREAM_PRIORITY)

    def test_blueprint_installs_beside_device_overlay(self):
        blueprint = (ROOT / "overlay" / self.MODULE / "Android.bp").read_text(encoding="utf-8")
        self.assertRegex(blueprint, r"runtime_resource_overlay\s*\{")
        self.assertIn(f'name: "{self.MODULE}"', blueprint)
        self.assertIn("device_specific: true", blueprint)

    def test_product_installs_module_only_for_salami(self):
        product = (ROOT / "product.mk").read_text(encoding="utf-8")
        gate = re.search(
            r"^ifeq \(\$\(TARGET_PRODUCT\),lineage_salami\)\n(.*?)^endif$",
            product, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(gate, "missing lineage_salami gate")
        self.assertRegex(gate.group(1),
                         rf"PRODUCT_PACKAGES \+=\s*\\?\s*{self.MODULE}\b")
        outside = product[:gate.start()] + product[gate.end():]
        self.assertNotIn(self.MODULE, outside)


if __name__ == "__main__":
    unittest.main()
