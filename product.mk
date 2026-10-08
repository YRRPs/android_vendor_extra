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
