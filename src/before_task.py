from __future__ import annotations

import sys
from pathlib import Path

from src import log
from src.proot_manager import ProotManager


def main() -> None:
    if len(sys.argv) < 3:
        log("Usage: python before_task.py <runner_path> <task_dir_name>")
        sys.exit(1)

    runner_path = Path(sys.argv[1])
    task_dir_name = sys.argv[2]

    manager = ProotManager(runner_path)

    if not manager.in_fifo.exists():
        log("Error: proot session not running (in.fifo not found)")
        sys.exit(1)

    log("Installing task dependencies...")
    manager.send_command(f"cd /mnt/runner/tasks/{task_dir_name}", 10)
    manager.send_command("poetry install")

    sys.exit(0)


if __name__ == "__main__":
    main()
