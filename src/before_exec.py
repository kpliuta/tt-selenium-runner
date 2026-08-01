from __future__ import annotations

import os
import sys
from pathlib import Path

from src import log
from src.proot_manager import ProotManager


def _env_bool(name: str) -> bool:
    return os.environ.get(name, "false") == "true"


def main() -> None:
    if len(sys.argv) < 2:
        log("Usage: python before_exec.py <runner_path>")
        sys.exit(1)

    runner_path = Path(sys.argv[1])
    manager = ProotManager(runner_path)
    manager.start_proot()

    # Verify container is ready by sending a simple echo command
    manager.send_command("echo 'Container is ready'", timeout=60)

    # Install/update container packages (idempotent — skips already-installed)
    log("Ensuring container packages are installed...")
    upgrade = str(_env_bool("VAR_UPGRADE_ON_STARTUP")).lower()
    manager.send_command(f"sh /mnt/runner/sh/setup_container.sh {upgrade}")

    # Install/update Firefox from official Mozilla repo
    log("Ensuring Firefox is installed from official Mozilla repo...")
    manager.send_command(f"sh /mnt/runner/sh/install_firefox.sh {upgrade}")

    # Export DISPLAY so VNC scripts run with a known display in the container
    manager.send_command("export DISPLAY=:1")

    # One-time VNC password and xstartup configuration
    log("Configuring VNC password and xstartup...")
    manager.send_command("sh /mnt/runner/sh/setup_vnc.sh", timeout=30)

    # Optionally terminate any running VNC server before starting a new one
    if _env_bool("VAR_TERMINATE_EXISTING_VNC"):
        log("Terminating existing VNC server...")
        manager.send_command("sh /mnt/runner/sh/terminate_vnc.sh", timeout=60)

    # Start VNC server inside the container
    log("Starting VNC server inside container...")
    manager.send_command("sh /mnt/runner/sh/start_vnc.sh", timeout=60)

    sys.exit(0)


if __name__ == "__main__":
    main()
