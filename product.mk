#
# SPDX-FileCopyrightText: Yim's Riced ROM Project
# SPDX-License-Identifier: Apache-2.0
#
# Inherited first by vendor/lineage/config/common.mk, so values set here
# take precedence over LineageOS defaults.

# Point the on-device Updater at the YRRP OTA server instead of
# download.lineageos.org, which never lists UNOFFICIAL builds.
PRODUCT_SYSTEM_PROPERTIES += \
    lineage.updater.uri=https://ota.yimura.dev/updates/{device}.json
