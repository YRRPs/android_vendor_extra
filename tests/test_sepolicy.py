"""Static checks of the boot animation sepolicy; m selinux_policy proves it compiles."""

import unittest
from pathlib import Path

POLICY = Path(__file__).resolve().parent.parent / "sepolicy" / "private"


def rules(name):
    lines = (POLICY / name).read_text(encoding="utf-8").splitlines()
    return [line.split("#")[0].strip() for line in lines if line.split("#")[0].strip()]


class SepolicyTest(unittest.TestCase):
    def test_types_are_product_internal(self):
        self.assertEqual(
            ["product_internal_prop(yrrp_bootanim_prop)",
             "product_internal_prop(yrrp_bootanim_status_prop)"],
            rules("property.te"))

    def test_contexts(self):
        self.assertEqual(
            [["persist.yrrp.bootanim.style", "u:object_r:yrrp_bootanim_prop:s0", "exact", "string"],
             ["persist.yrrp.bootanim.full_intro", "u:object_r:yrrp_bootanim_prop:s0", "exact",
              "bool"],
             ["sys.yrrp.bootanim.", "u:object_r:yrrp_bootanim_status_prop:s0"]],
            [line.split() for line in rules("property_contexts")])

    def test_access_matrix(self):
        self.assertEqual(["set_prop(system_app, yrrp_bootanim_prop)"], rules("system_app.te"))
        self.assertEqual(
            ["get_prop(bootanim, yrrp_bootanim_prop)",
             "set_prop(bootanim, yrrp_bootanim_status_prop)"],
            rules("bootanim.te"))
        self.assertEqual(
            ["set_prop(shell, yrrp_bootanim_prop)",
             "get_prop(shell, yrrp_bootanim_status_prop)"],
            rules("shell.te"))


if __name__ == "__main__":
    unittest.main()
