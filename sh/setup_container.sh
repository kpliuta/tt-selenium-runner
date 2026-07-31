#!/bin/sh
set -e

UPGRADE=${1:-false}
export DEBIAN_FRONTEND=noninteractive

echo "Applying fix for gtk-update-icon-cache hang inside proot..."
dpkg-divert --divert /usr/bin/gtk-update-icon-cache.distrib --rename /usr/bin/gtk-update-icon-cache 2>/dev/null || true
ln -sf /bin/true /usr/bin/gtk-update-icon-cache 2>/dev/null || true

echo "Updating container package lists..."
apt-get update -qq

if [ "$UPGRADE" = "true" ]; then
    echo "Upgrading installed container packages..."
    apt-get dist-upgrade -y -qq -o Dpkg::Options::="--force-confdef"
    echo "Removing unused packages..."
    apt-get autoremove -y -qq
fi

echo "Checking container dependencies..."
for pkg in wget xfce4 dbus-x11 tightvncserver python3-poetry ffmpeg; do
    if ! dpkg -s "$pkg" >/dev/null 2>&1; then
        echo "  Installing $pkg..."
        apt-get install -y -qq "$pkg"
    fi
done

echo "Container dependencies are up to date."
