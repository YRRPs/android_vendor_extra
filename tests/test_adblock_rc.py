"""Static checks of the ad-blocking init fragment; the device proves init runs it."""

import unittest
from pathlib import Path

RC = Path(__file__).resolve().parent.parent / "init" / "yrrp_adblock.rc"
LIVE = "/data/misc/yrrp/hosts"


def blocks():
    """Maps each trigger header to its command lines, comments and blanks dropped."""
    result, current = {}, None
    for raw in RC.read_text(encoding="utf-8").splitlines():
        line = raw.split("#")[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" "):
            current = line.strip()
            result[current] = []
        else:
            result[current].append(" ".join(line.split()))
    return result


class AdblockRcTest(unittest.TestCase):
    def test_post_fs_data_seeds_and_mounts(self):
        self.assertEqual(
            ["mkdir /data/misc/yrrp 0771 system system",
             "copy /system/etc/hosts /data/misc/yrrp/hosts.stock",
             "copy /system/etc/hosts /data/misc/yrrp/hosts",
             "chmod 0644 /data/misc/yrrp/hosts.stock",
             "chmod 0644 /data/misc/yrrp/hosts",
             "restorecon_recursive /data/misc/yrrp",
             "mount none /data/misc/yrrp/hosts /system/etc/hosts bind"],
            blocks()["on post-fs-data"])

    def test_triggers_copy_in_place(self):
        blocked = [f"copy /data/misc/yrrp/hosts.blocked {LIVE}"]
        self.assertEqual(
            {"on post-fs-data",
             "on boot && property:persist.yrrp.adblock.enabled=1",
             "on property:persist.yrrp.adblock.enabled=1",
             "on property:persist.yrrp.adblock.enabled=0",
             "on property:sys.yrrp.adblock.apply=* && property:persist.yrrp.adblock.enabled=1"},
            set(blocks()))
        b = blocks()
        self.assertEqual(blocked, b["on boot && property:persist.yrrp.adblock.enabled=1"])
        self.assertEqual(blocked, b["on property:persist.yrrp.adblock.enabled=1"])
        self.assertEqual([f"copy /data/misc/yrrp/hosts.stock {LIVE}"],
                         b["on property:persist.yrrp.adblock.enabled=0"])
        self.assertEqual(
            blocked,
            b["on property:sys.yrrp.adblock.apply=* && property:persist.yrrp.adblock.enabled=1"])

    def test_never_writes_system(self):
        for commands in blocks().values():
            for command in commands:
                words = command.split()
                self.assertNotIn("remount", words)
                self.assertNotIn("rw", words)
                if words[0] in ("copy", "write", "chmod", "chown"):
                    self.assertTrue(words[-1].startswith("/data/misc/yrrp/"), command)

if __name__ == "__main__":
    unittest.main()
