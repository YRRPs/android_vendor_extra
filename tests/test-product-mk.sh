#!/bin/bash
# Evaluate product.mk with stubbed product functions; no Android tree needed.
set -euo pipefail
repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
scratch=$(mktemp -d)
trap 'rm -rf "${scratch}"' EXIT

# Make has no quoting; backslash-escape spaces so odd checkout paths work.
make_repo=${repo// /\\ }

cat > "${scratch}/harness.mk" <<EOF
inherit-product = \$(eval INHERITED += \$(1))
TARGET_COPY_OUT_PRODUCT := product
include ${make_repo}/product.mk
show:
	@printf 'props=%s\n' "\$(strip \$(PRODUCT_SYSTEM_PROPERTIES))"
	@printf 'productprops=%s\n' "\$(strip \$(PRODUCT_PRODUCT_PROPERTIES))"
	@printf 'inherited=%s\n' "\$(strip \$(INHERITED))"
	@printf 'sepolicy=%s\n' "\$(strip \$(PRODUCT_PRIVATE_SEPOLICY_DIRS))"
	@printf 'packages=%s\n' "\$(strip \$(PRODUCT_PACKAGES))"
	@printf 'copy=%s\n' "\$(strip \$(PRODUCT_COPY_FILES))"
EOF

run() { env -u YRRP_BUILD_TYPE "$@" make --no-print-directory -f "${scratch}/harness.mk" show; }

vanilla=$(run)
grep -Eq 'ro.yrrp.build.type=vanilla( |$)' <<<"${vanilla}"
grep -q 'lineage.updater.uri=https://ota.yimura.dev/updates/{device}/{incr}.json' <<<"${vanilla}"
grep -q '^inherited=$' <<<"${vanilla}"
grep -Eq 'ro.init.shutdown_animation=true( |$)' <<<"${vanilla}"
grep -q '^sepolicy=vendor/extra/sepolicy/private$' <<<"${vanilla}"
grep -q '^copy=vendor/extra/init/yrrp_adblock.rc:product/etc/init/yrrp_adblock.rc$' <<<"${vanilla}"

gapps=$(run YRRP_BUILD_TYPE=gapps)
grep -Eq 'ro.yrrp.build.type=gapps( |$)' <<<"${gapps}"
grep -q 'lineage.updater.uri=https://ota.yimura.dev/updates/{device}/gapps/{incr}.json' <<<"${gapps}"
grep -q '^inherited=vendor/gapps/arm64/arm64-vendor.mk$' <<<"${gapps}"
grep -Eq 'ro.init.shutdown_animation=true( |$)' <<<"${gapps}"
grep -q '^copy=vendor/extra/init/yrrp_adblock.rc:product/etc/init/yrrp_adblock.rc$' <<<"${gapps}"

expect_rejected() {
    local value=$1
    if run "YRRP_BUILD_TYPE=${value}" >"${scratch}/bad.out" 2>&1; then
        echo "YRRP_BUILD_TYPE='${value}' must fail" >&2
        exit 1
    fi
    grep -qF "YRRP_BUILD_TYPE must be vanilla or gapps, got '${value}'" "${scratch}/bad.out"
}

xueying=$(run TARGET_PRODUCT=lineage_xueying)
grep -Eq '^packages=(.* )?YrrpXueyingUnfold( |$)' <<<"${xueying}"
grep -Eq '^productprops=(.* )?persist.fold_lock_setting_enabled=true( |$)' <<<"${xueying}"
if grep -q 'YrrpSalamiAutoBrightness' <<<"${xueying}"; then
    echo 'salami overlay must not install on xueying' >&2; exit 1
fi
salami=$(run TARGET_PRODUCT=lineage_salami)
if grep -q 'YrrpXueyingUnfold' <<<"${salami}"; then
    echo 'xueying unfold overlay must not install on salami' >&2; exit 1
fi
if grep -q 'fold_lock_setting_enabled' <<<"${salami}${vanilla}"; then
    echo 'fold-lock property must only be set on xueying' >&2; exit 1
fi

expect_rejected 'kernelsu'
expect_rejected ''
expect_rejected 'gapps '
expect_rejected ' gapps'
expect_rejected 'vanilla gapps'
expect_rejected '] [gapps'
expect_rejected 'x] [vanilla'
expect_rejected $'gapps\t'
expect_rejected $'\tgapps'
expect_rejected $'vanilla\t'
printf 'product.mk type selection passed\n'
