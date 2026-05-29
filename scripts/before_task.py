from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.proot_manager import ProotManager


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python before_task.py <runner_path> <task_dir_name>", file=sys.stderr)
        sys.exit(1)

    runner_path = Path(sys.argv[1])
    task_dir_name = sys.argv[2]

    manager = ProotManager(runner_path)

    if not manager.in_fifo.exists():
        print("Error: proot session not running (in.fifo not found)", file=sys.stderr)
        sys.exit(1)

    cmd = f"cd /mnt/runner/tasks/{task_dir_name} && poetry install"
    print(f"Installing task dependencies: {cmd}")
    manager.send_command(cmd)

    sys.exit(0)


if __name__ == "__main__":
    main()
