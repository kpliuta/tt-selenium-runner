from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.proot_manager import ProotManager


def _should_upgrade() -> bool:
    return os.environ.get("VAR_UPGRADE_ON_STARTUP", "false") == "true"


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python before_exec.py <runner_path>", file=sys.stderr)
        sys.exit(1)

    runner_path = Path(sys.argv[1])
    manager = ProotManager(runner_path)
    manager.start_proot()

    # Verify container is ready by sending a simple echo command
    manager.send_command("echo 'Container is ready'", timeout=60)

    # Install/update container packages (idempotent — skips already-installed)
    print("Ensuring container packages are installed...")
    upgrade = str(_should_upgrade()).lower()
    manager.send_command(f"sh /mnt/runner/scripts/sh/setup_container.sh {upgrade}")

    # One-time VNC password and xstartup configuration
    print("Configuring VNC password and xstartup...")
    manager.send_command("sh /mnt/runner/scripts/sh/setup_vnc.sh", timeout=30)

    # Start VNC server inside the container
    print("Starting VNC server inside container...")
    manager.send_command("sh /mnt/runner/scripts/sh/start_vnc.sh", timeout=60)

    print("VNC server started successfully")
    sys.exit(0)


if __name__ == "__main__":
    main()
