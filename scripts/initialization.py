from __future__ import annotations

import subprocess
import sys

from scripts import log


def _run(cmd: list[str], check: bool = True, timeout: int | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, timeout=timeout)


def _is_termux() -> bool:
    import os
    return "TERMUX_VERSION" in os.environ


def _is_proot_distro_installed() -> bool:
    result = subprocess.run(["dpkg", "-s", "proot-distro"], capture_output=True, text=True)
    return result.returncode == 0


def _is_ubuntu_installed() -> bool:
    result = subprocess.run(
        ["proot-distro", "login", "ubuntu", "--", "true"],
        capture_output=True, timeout=30,
    )
    return result.returncode == 0


def main() -> None:
    if not _is_termux():
        log("Error: must run in Termux environment")
        sys.exit(1)

    if not _is_proot_distro_installed():
        log("Installing proot-distro...")
        _run(["apt-get", "install", "-y", "proot-distro"])
    else:
        log("proot-distro already installed")

    if not _is_ubuntu_installed():
        log("Installing proot-distro Ubuntu container...")
        result = _run(["proot-distro", "install", "ubuntu"], check=False)
        if result.returncode != 0:
            log(f"proot-distro install failed: {result.stderr}")
            sys.exit(result.returncode)
    else:
        log("Ubuntu container already installed")

    log("Initialization complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()
