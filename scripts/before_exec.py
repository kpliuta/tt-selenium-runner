from __future__ import annotations

import os
import sys
from pathlib import Path

from scripts import log
from scripts.proot_manager import ProotManager


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
    manager.send_command(f"sh /mnt/runner/scripts/sh/setup_container.sh {upgrade}")

    # One-time VNC password and xstartup configuration
    log("Configuring VNC password and xstartup...")
    manager.send_command("sh /mnt/runner/scripts/sh/setup_vnc.sh", timeout=30)

    # Optionally terminate any running VNC server before starting a new one
    if _env_bool("VAR_TERMINATE_EXISTING_VNC"):
        log("Terminating existing VNC server...")
        manager.send_command("sh /mnt/runner/scripts/sh/terminate_vnc.sh", timeout=60)

    # Start VNC server inside the container
    log("Starting VNC server inside container...")
    manager.send_command("sh /mnt/runner/scripts/sh/start_vnc.sh", timeout=60)

    sys.exit(0)


if __name__ == "__main__":
    main()
