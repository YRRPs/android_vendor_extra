# android_vendor_extra

YRRP product overrides, checked out at `vendor/extra`.

LineageOS inherits `vendor/extra/product.mk` before its own common
configuration (`vendor/lineage/config/common.mk`), so properties set here win.

| Property | Value | Why |
|---|---|---|
| `ro.yrrp.build.type` | `vanilla` (default) or `gapps` | Records the build type. `ro.lineage.releasetype` cannot hold it, because LineageOS turns custom values back into UNOFFICIAL. |
| `lineage.updater.uri` | vanilla: `https://ota.yimura.dev/updates/{device}/{incr}.json`<br>gapps: `https://ota.yimura.dev/updates/{device}/gapps/{incr}.json` | The Updater substitutes `{device}` (`salami`) and `{incr}`, and otherwise queries download.lineageos.org, which never lists UNOFFICIAL builds. Each type is its own OTA channel with its own incremental chain. |

The `gapps` type also inherits `vendor/gapps/arm64/arm64-vendor.mk`.
`YRRP_BUILD_TYPE` must be `vanilla` or `gapps`; any other value stops the
build with an error.

## Build a type

```bash
YRRP_BUILD_TYPE=gapps breakfast salami
```

Leave `YRRP_BUILD_TYPE` unset for `vanilla`. Verify on a built tree:

```bash
grep -E 'ro.yrrp.build.type|lineage.updater.uri' out/target/product/salami/system/build.prop
```

`tests/test-product-mk.sh` evaluates `product.mk` with GNU Make outside the
Android tree and checks both types plus the unknown-type error.

## Salami indoor auto-brightness

`overlay/YrrpSalamiAutoBrightness` is a static runtime resource overlay on
`android` (priority 360). It wins over the salami device overlay
`android.overlay.oplus.target` (priority 350). `product.mk` installs it only
when `TARGET_PRODUCT` is `lineage_salami`.

The overlay keeps the upstream nits targets and stretches the lux break points
by a divisor `D`. Indoors (1000 lux and below) the curve sees `lux / D`.
Between 1000 and 10000 lux the divisor tapers logarithmically to 1, and from
10000 lux upward the curve matches upstream.

`tools/autobrightness/gen_overlay.py` writes the overlay from a pinned copy of
the upstream curve, `tools/autobrightness/upstream-salami-config.xml`. To
retune, regenerate with a new `--divisor`; the overlay header records `D`,
and the tests check the overlay against that value. `D` must be at least 1
and below 10, or the lux points stop increasing and the generator refuses.

```bash
tools/autobrightness/gen_overlay.py --divisor 5
python3 -m unittest discover -s tests
```

If the upstream curve changes, refresh the snapshot and `UPSTREAM_SOURCE` in
the generator, then regenerate.

Verify on salami:

```bash
adb shell cmd overlay list android
adb shell dumpsys display | grep -A3 mDefaultConfig
```
