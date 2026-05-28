#!/bin/sh
set -e

UPGRADE=${1:-false}

# Prevent hangs during gtk-update-icon-cache (broken inside proot-distro
# because it tries to read /proc/self/exe which fails).  Divert to /bin/true.
dpkg-divert --divert /usr/bin/gtk-update-icon-cache.distrib --rename /usr/bin/gtk-update-icon-cache 2>/dev/null || true
ln -sf /bin/true /usr/bin/gtk-update-icon-cache 2>/dev/null || true

export DEBIAN_FRONTEND=noninteractive

if [ "$UPGRADE" = "true" ]; then
    apt-get update -qq
    apt-get dist-upgrade -y -qq -o Dpkg::Options::="--force-confdef"
    apt-get autoremove -y -qq
fi

for pkg in wget xfce4 dbus-x11 tightvncserver firefox python3-poetry ffmpeg; do
    if ! dpkg -s "$pkg" >/dev/null 2>&1; then
        apt-get install -y -qq "$pkg"
    fi
done
