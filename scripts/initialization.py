from __future__ import annotations

import subprocess
import sys


def _run(cmd: list[str], check: bool = True, timeout: int | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, timeout=timeout)


def _is_termux() -> bool:
    import os
    return "TERMUX_VERSION" in os.environ


def _is_proot_distro_installed() -> bool:
    result = subprocess.run(["dpkg", "-s", "proot-distro"], capture_output=True, text=True)
    return result.returncode == 0


def _is_ubuntu_installed() -> bool:
    result = subprocess.run(["proot-distro", "list"], capture_output=True, text=True)
    return "ubuntu" in result.stdout


def main() -> None:
    if not _is_termux():
        print("Error: must run in Termux environment", file=sys.stderr)
        sys.exit(1)

    if not _is_proot_distro_installed():
        print("Installing proot-distro...")
        _run(["apt-get", "install", "-y", "proot-distro"])
    else:
        print("proot-distro already installed")

    if not _is_ubuntu_installed():
        print("Installing proot-distro Ubuntu container...")
        result = _run(["proot-distro", "install", "ubuntu"], check=False)
        if result.returncode != 0:
            print(f"proot-distro install failed: {result.stderr}", file=sys.stderr)
            sys.exit(result.returncode)
    else:
        print("Ubuntu container already installed")

    print("Initialization complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()
