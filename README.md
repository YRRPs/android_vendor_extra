# android_vendor_extra

YRRP product overrides, checked out at `vendor/extra`.

LineageOS inherits `vendor/extra/product.mk` before its own common
configuration (`vendor/lineage/config/common.mk`), so properties set here win.

| Property | Value | Why |
|---|---|---|
| `ro.yrrp.build.type` | `vanilla` (default) or `gapps` | Records the build type. `ro.lineage.releasetype` cannot hold it, because LineageOS turns custom values back into UNOFFICIAL. |
| `lineage.updater.uri` | vanilla: `https://ota.yimura.dev/updates/{device}/{incr}.json`<br>gapps: `https://ota.yimura.dev/updates/{device}/gapps/{incr}.json` | The Updater substitutes `{device}` (`salami`) and `{incr}`, and otherwise queries download.lineageos.org, which never lists UNOFFICIAL builds. Each type is its own OTA channel with its own incremental chain. |

The `gapps` type also inherits `vendor/gapps/arm64/arm64-vendor.mk`.
`YRRP_BUILD_TYPE` must be exactly `vanilla` or `gapps` (unset means
`vanilla`); any other value, including an empty or whitespace-padded one,
stops the build with an error.

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

## Boot animation

`product.mk` sets `ro.init.shutdown_animation=true`, so init runs
bootanimation on shutdown and reboot as well as on boot, and adds
`sepolicy/private` to `PRODUCT_PRIVATE_SEPOLICY_DIRS`.

The Matrix boot animation uses two property namespaces:

| Namespace | Type | Meaning |
|---|---|---|
| `persist.yrrp.bootanim.style` (exact, string) and `persist.yrrp.bootanim.full_intro` (exact, bool) | `yrrp_bootanim_prop` | The style chosen in YRRPs Settings and the full-intro switch. Settings writes them, bootanimation reads them. |
| `sys.yrrp.bootanim.*` (prefix) | `yrrp_bootanim_status_prop` | Route and result that bootanimation publishes, for acceptance checks over adb. |

Both types are declared with `product_internal_prop`, so only core domains
may touch them. Access matrix:

| Domain | `yrrp_bootanim_prop` (`persist.yrrp.bootanim.*`) | `yrrp_bootanim_status_prop` (`sys.yrrp.bootanim.*`) |
|---|---|---|
| `system_app` (Settings) | set (implies read) | none |
| `bootanim` | read | set |
| `shell` | set (acceptance, restoration) | read |

`tests/test_sepolicy.py` checks these rules statically; only `m selinux_policy`
proves they compile. If product policy cannot grant rules to platform
domains, move `sepolicy/private` to `SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS`.
