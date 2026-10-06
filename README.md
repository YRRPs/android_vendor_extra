# android_vendor_extra

YRRP product overrides, checked out at `vendor/extra`.

LineageOS inherits `vendor/extra/product.mk` before its own common
configuration (`vendor/lineage/config/common.mk`), so properties set here win.

| Property | Value | Why |
|---|---|---|
| `lineage.updater.uri` | `https://ota.yimura.dev/updates/{device}.json` | The Updater substitutes `{device}` (`salami`) and otherwise queries download.lineageos.org, which never lists UNOFFICIAL builds. |

Verify on a built tree:

```bash
grep lineage.updater.uri out/target/product/salami/system/build.prop
```
