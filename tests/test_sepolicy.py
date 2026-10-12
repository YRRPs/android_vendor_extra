"""Static checks of the YRRP product sepolicy; m selinux_policy proves it compiles."""

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
             "product_internal_prop(yrrp_bootanim_status_prop)",
             "product_internal_prop(yrrp_adblock_prop)"],
            rules("property.te"))

    def test_contexts(self):
        self.assertEqual(
            [["persist.yrrp.bootanim.style", "u:object_r:yrrp_bootanim_prop:s0", "exact", "string"],
             ["persist.yrrp.bootanim.full_intro", "u:object_r:yrrp_bootanim_prop:s0", "exact",
              "bool"],
             ["sys.yrrp.bootanim.", "u:object_r:yrrp_bootanim_status_prop:s0"],
             ["persist.yrrp.adblock.enabled", "u:object_r:yrrp_adblock_prop:s0", "exact", "bool"],
             ["sys.yrrp.adblock.apply", "u:object_r:yrrp_adblock_prop:s0", "exact", "int"]],
            [line.split() for line in rules("property_contexts")])

    def test_adblock_file_types(self):
        self.assertEqual(
            ["type yrrp_adblock_data_file, file_type, data_file_type, core_data_file_type;",
             "type yrrp_hosts_file, file_type, data_file_type, core_data_file_type;"],
            rules("file.te"))
        self.assertEqual(
            [["/data/misc/yrrp(/.*)?", "u:object_r:yrrp_adblock_data_file:s0"],
             ["/data/misc/yrrp/hosts", "u:object_r:yrrp_hosts_file:s0"],
             ["/data/misc/yrrp/hosts\\.stock", "u:object_r:yrrp_hosts_file:s0"]],
            [line.split() for line in rules("file_contexts")])

    def test_access_matrix(self):
        self.assertEqual(
            ["set_prop(system_app, yrrp_bootanim_prop)",
             "set_prop(system_app, yrrp_adblock_prop)",
             "allow system_app yrrp_adblock_data_file:dir rw_dir_perms;",
             "allow system_app yrrp_adblock_data_file:file create_file_perms;"],
            rules("system_app.te"))
        self.assertEqual(
            ["allow init system_file:file mounton;",
             "allow init yrrp_adblock_data_file:dir { create_dir_perms relabelfrom relabelto };",
             "allow init yrrp_adblock_data_file:file { r_file_perms relabelfrom relabelto };",
             "allow init yrrp_hosts_file:file { create_file_perms relabelfrom relabelto };"],
            rules("init.te"))
        self.assertEqual(
            ["allow { coredomain -mediaextractor -perfetto -traced -traced_probes }"
             " yrrp_hosts_file:file r_file_perms;"],
            rules("coredomain.te"))
        self.assertEqual(
            ["get_prop(bootanim, yrrp_bootanim_prop)",
             "set_prop(bootanim, yrrp_bootanim_status_prop)"],
            rules("bootanim.te"))
        self.assertEqual(
            ["set_prop(shell, yrrp_bootanim_prop)",
             "get_prop(shell, yrrp_bootanim_status_prop)",
             "set_prop(shell, yrrp_adblock_prop)"],
            rules("shell.te"))

    def test_live_hosts_read_skips_neverallowed_domains(self):
        # AOSP neverallows these domains from opening data files (their .te files in
        # system/sepolicy/private). None is a net_domain, so none resolves names.
        rule = rules("coredomain.te")[0]
        for domain in ("mediaextractor", "perfetto", "traced", "traced_probes"):
            self.assertIn(" -" + domain + " ", rule + " ")

    def test_system_app_cannot_write_live_hosts(self):
        text = (POLICY / "system_app.te").read_text(encoding="utf-8")
        self.assertNotIn("yrrp_hosts_file", text)

if __name__ == "__main__":
    unittest.main()
