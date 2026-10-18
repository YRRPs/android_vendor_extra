#
# SPDX-FileCopyrightText: Yim's Riced ROM Project
# SPDX-License-Identifier: Apache-2.0
#
# Inherited first by vendor/lineage/config/common.mk, so values set here
# take precedence over LineageOS defaults.

# Build type, chosen by the YRRP signer through YRRP_BUILD_TYPE. Each type is
# its own OTA channel: the Updater URI below is baked per type, and the OTA
# server keeps one incremental chain per channel. {incr} lets the server answer
# a device on the channel's previous build with an incremental OTA; every other
# build falls back to the channel's full OTA. ro.lineage.releasetype cannot hold
# the type, because LineageOS turns custom values back into UNOFFICIAL.
YRRP_BUILD_TYPE ?= vanilla
ifeq ($(YRRP_BUILD_TYPE),vanilla)
PRODUCT_SYSTEM_PROPERTIES += \
    lineage.updater.uri=https://ota.yimura.dev/updates/{device}/{incr}.json
else ifeq ($(YRRP_BUILD_TYPE),gapps)
$(call inherit-product, vendor/gapps/arm64/arm64-vendor.mk)
# Privileged permissions newer GmsCore needs and MindTheGapps baklava lacks.
PRODUCT_COPY_FILES += \
    vendor/extra/permissions/privapp-permissions-yrrp-gms.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/permissions/privapp-permissions-yrrp-gms.xml
PRODUCT_SYSTEM_PROPERTIES += \
    lineage.updater.uri=https://ota.yimura.dev/updates/{device}/gapps/{incr}.json
else
$(error YRRP_BUILD_TYPE must be vanilla or gapps, got '$(YRRP_BUILD_TYPE)')
endif

PRODUCT_SYSTEM_PROPERTIES += \
    ro.yrrp.build.type=$(YRRP_BUILD_TYPE)

# Dim indoor auto-brightness on salami without changing daylight. The curve
# is salami-specific, and this file applies to every device. Product
# makefiles are evaluated in isolation, so PRODUCT_DEVICE is not visible
# here; gate on the lunch target instead. A second salami product name
# would need adding to this check.
ifeq ($(TARGET_PRODUCT),lineage_salami)
PRODUCT_PACKAGES += \
    YrrpSalamiAutoBrightness
endif

# Matrix boot animation (frameworks/base cmds/bootanimation). init restarts the
# animation class during shutdown only when this property is true. The product
# sepolicy lets YRRPs Settings write persist.yrrp.bootanim.*, bootanimation read
# it, and bootanimation publish its sys.yrrp.bootanim.* status.
PRODUCT_SYSTEM_PROPERTIES += \
    ro.init.shutdown_animation=true
PRODUCT_PRIVATE_SEPOLICY_DIRS += vendor/extra/sepolicy/private

# Turn on AOSP's hinge-driven fold/unfold framework on the OnePlus Open. The
# YRRPs Fold animation setting chooses Stock, Pixel or Duo in SystemUI; Stock
# (the default) suppresses every unfold animation. Gate on the lunch target for
# the same reason as the salami overlay above. The overlay also sets
# config_fold_lock_behavior, and the property below passes the fold-lock flag gate on
# userdebug builds, so Android honours "Continue using apps on fold" here.
ifeq ($(TARGET_PRODUCT),lineage_xueying)
PRODUCT_PACKAGES += \
    YrrpXueyingUnfold
PRODUCT_PRODUCT_PROPERTIES += \
    persist.fold_lock_setting_enabled=true
endif

# Hosts-file ad blocking (YRRPs Settings > Network > Ad blocking). init bind-mounts
# /data/misc/yrrp/hosts over /system/etc/hosts, so /system stays read-only.
PRODUCT_COPY_FILES += \
    vendor/extra/init/yrrp_adblock.rc:$(TARGET_COPY_OUT_PRODUCT)/etc/init/yrrp_adblock.rc
