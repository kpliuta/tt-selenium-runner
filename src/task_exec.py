from __future__ import annotations

import sys
from pathlib import Path

from src import log
from src.proot_manager import ProotManager


def main() -> None:
    if len(sys.argv) < 3:
        log("Usage: python task_exec.py <runner_path> <task_dir_name>")
        sys.exit(1)

    runner_path = Path(sys.argv[1])
    task_dir_name = sys.argv[2]

    manager = ProotManager(runner_path)

    if not manager.in_fifo.exists():
        log("Error: proot session not running (in.fifo not found)")
        sys.exit(1)

    mnt_task = f"/mnt/runner/tasks/{task_dir_name}"
    output_dir = f"{mnt_task}/output"

    log("Running task...")
    manager.send_command(f"cd {mnt_task}", 10)
    manager.send_command(f"export MNT_OUTPUT_DIR={output_dir}", 10)
    manager.send_command("poetry run python src/main.py", timeout=600)

    sys.exit(0)


if __name__ == "__main__":
    main()
