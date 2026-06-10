#!/bin/sh
set -e

UPGRADE=${1:-false}
export DEBIAN_FRONTEND=noninteractive

if [ ! -f /etc/apt/sources.list.d/mozilla.sources ]; then
    echo "Setting up official Mozilla repository for Firefox..."

    # Add the Mozilla signing key
    wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- | gpg --dearmor | tee /etc/apt/keyrings/packages.mozilla.org.gpg > /dev/null

    # Add the Mozilla apt repository
    echo "Types: deb
URIs: https://packages.mozilla.org/apt
Suites: mozilla
Components: main
Signed-By: /etc/apt/keyrings/packages.mozilla.org.gpg" | tee /etc/apt/sources.list.d/mozilla.sources

    # Set APT priority so Mozilla's Firefox is preferred over Ubuntu's snap transitional package
    echo "Package: firefox*
Pin: origin packages.mozilla.org
Pin-Priority: 1001" | tee /etc/apt/preferences.d/mozilla

    # Clear package cache then update to avoid stale/400 errors from Mozilla repo
    apt-get clean
    apt-get update -qq
fi


if command -v firefox >/dev/null 2>&1; then
    echo "Firefox is already installed."
    if [ "$UPGRADE" = "true" ]; then
        echo "Upgrading Firefox to the latest version..."

        # Clear package cache then update to avoid stale/400 errors from Mozilla repo
        apt-get clean
        apt-get update -qq

        apt-get install --only-upgrade -y -qq firefox
    fi
else
    echo "Installing Firefox from Mozilla official repository..."
    apt-get install -y -qq firefox
fi
