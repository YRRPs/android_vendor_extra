#
# SPDX-FileCopyrightText: Yim's Riced ROM Project
# SPDX-License-Identifier: Apache-2.0
#
# Inherited first by vendor/lineage/config/common.mk, so values set here
# take precedence over LineageOS defaults.

# Point the on-device Updater at the YRRP OTA server instead of
# download.lineageos.org, which never lists UNOFFICIAL builds. {incr} lets
# the server answer a device on the previous build with an incremental OTA;
# every other build falls back to the full OTA.
PRODUCT_SYSTEM_PROPERTIES += \
    lineage.updater.uri=https://ota.yimura.dev/updates/{device}/{incr}.json

# Dim indoor auto-brightness on salami without changing daylight. The curve
# is salami-specific, and this file applies to every device. Product
# makefiles are evaluated in isolation, so PRODUCT_DEVICE is not visible
# here; gate on the lunch target instead. A second salami product name
# would need adding to this check.
ifeq ($(TARGET_PRODUCT),lineage_salami)
PRODUCT_PACKAGES += \
    YrrpSalamiAutoBrightness
endif
