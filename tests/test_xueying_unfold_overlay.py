#
# SPDX-FileCopyrightText: Yim's Riced ROM Project
# SPDX-License-Identifier: Apache-2.0
#
"""Checks the xueying unfold overlay turns on exactly the unfold framework and fold lock."""

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "overlay" / "YrrpXueyingUnfold"
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


class XueyingUnfoldOverlayTest(unittest.TestCase):
    def test_sets_exactly_the_unfold_and_fold_lock_booleans(self):
        root = ET.parse(OVERLAY / "res" / "values" / "config.xml").getroot()
        values = {item.get("name"): item.text.strip() for item in root}
        self.assertEqual(values, {
            "config_unfoldTransitionEnabled": "true",
            "config_unfoldTransitionHingeAngle": "true",
            "config_fold_lock_behavior": "true",
        })

    def test_overlays_android_above_the_device_overlay(self):
        manifest = ET.parse(OVERLAY / "AndroidManifest.xml").getroot()
        self.assertEqual(manifest.get("package"), "org.yrrp.overlay.xueying.unfold")
        overlay = manifest.find("overlay")
        self.assertEqual(overlay.get(ANDROID_NS + "targetPackage"), "android")
        self.assertEqual(overlay.get(ANDROID_NS + "isStatic"), "true")
        self.assertEqual(overlay.get(ANDROID_NS + "priority"), "360")

    def test_blueprint_declares_device_specific_rro(self):
        bp = (OVERLAY / "Android.bp").read_text()
        self.assertIn("runtime_resource_overlay {", bp)
        self.assertIn('name: "YrrpXueyingUnfold"', bp)
        self.assertIn("device_specific: true", bp)


if __name__ == "__main__":
    unittest.main()
