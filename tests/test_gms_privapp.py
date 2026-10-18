"""Static checks of the GMS privileged-permission allowlist; the device proves the grants."""

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

XML = (Path(__file__).resolve().parent.parent
       / "permissions" / "privapp-permissions-yrrp-gms.xml")

# Privileged permissions GmsCore 26.40.32 requests that MindTheGapps baklava
# (39bd3a0964) does not allowlist; cinnamonbun allowlists exactly these.
EXPECTED = {
    "android.permission.GET_ROLE_HOLDERS",
    "android.permission.LOG_COMPAT_CHANGE",
    "android.permission.MANAGE_SECURE_LOCK_DEVICE",
    "android.permission.OBSERVE_ROLE_HOLDERS",
    "android.permission.READ_COMPAT_CHANGE_CONFIG",
}


class GmsPrivappTest(unittest.TestCase):
    def setUp(self):
        self.root = ET.parse(XML).getroot()

    def test_root_is_permissions(self):
        self.assertEqual("permissions", self.root.tag)

    def test_only_gms_is_allowlisted(self):
        packages = [e.get("package") for e in self.root]
        self.assertEqual(["com.google.android.gms"], packages)
        self.assertEqual("privapp-permissions", self.root[0].tag)

    def test_grants_exactly_the_missing_permissions(self):
        entries = list(self.root[0])
        self.assertTrue(all(e.tag == "permission" for e in entries))
        names = [e.get("name") for e in entries]
        self.assertEqual(len(names), len(set(names)), "duplicate permission")
        self.assertEqual(EXPECTED, set(names))

    def test_never_denies(self):
        self.assertEqual([], self.root.findall(".//deny-permission"))


if __name__ == "__main__":
    unittest.main()
