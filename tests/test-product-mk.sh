#!/bin/bash
# Evaluate product.mk with stubbed product functions; no Android tree needed.
set -euo pipefail
repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
scratch=$(mktemp -d)
trap 'rm -rf "${scratch}"' EXIT

cat > "${scratch}/harness.mk" <<EOF
inherit-product = \$(eval INHERITED += \$(1))
include ${repo}/product.mk
show:
	@printf 'props=%s\n' "\$(strip \$(PRODUCT_SYSTEM_PROPERTIES))"
	@printf 'inherited=%s\n' "\$(strip \$(INHERITED))"
EOF

run() { env -u YRRP_BUILD_TYPE "$@" make --no-print-directory -f "${scratch}/harness.mk" show; }

vanilla=$(run)
grep -q 'ro.yrrp.build.type=vanilla' <<<"${vanilla}"
grep -q 'lineage.updater.uri=https://ota.yimura.dev/updates/{device}/{incr}.json' <<<"${vanilla}"
grep -q '^inherited=$' <<<"${vanilla}"

gapps=$(run YRRP_BUILD_TYPE=gapps)
grep -q 'ro.yrrp.build.type=gapps' <<<"${gapps}"
grep -q 'lineage.updater.uri=https://ota.yimura.dev/updates/{device}/gapps/{incr}.json' <<<"${gapps}"
grep -q '^inherited=vendor/gapps/arm64/arm64-vendor.mk$' <<<"${gapps}"

if run YRRP_BUILD_TYPE=kernelsu >"${scratch}/bad.out" 2>&1; then
    echo 'unknown YRRP_BUILD_TYPE must fail' >&2
    exit 1
fi
grep -q 'YRRP_BUILD_TYPE must be vanilla or gapps' "${scratch}/bad.out"
printf 'product.mk type selection passed\n'
