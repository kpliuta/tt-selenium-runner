from __future__ import annotations

import sys
from pathlib import Path

# termux-tasker runs scripts with cwd=runner_path, adding only scripts/ to sys.path.
# Add the runner root so scripts.xxx imports resolve correctly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.proot_manager import ProotManager


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python task_exec.py <runner_path> <task_dir_name>", file=sys.stderr)
        sys.exit(1)

    runner_path = Path(sys.argv[1])
    task_dir_name = sys.argv[2]

    manager = ProotManager(runner_path)

    if not manager.in_fifo.exists():
        print("Error: proot session not running (in.fifo not found)", file=sys.stderr)
        sys.exit(1)

    mnt_task = f"/mnt/runner/tasks/{task_dir_name}"
    output_dir = f"{mnt_task}/output"

    cmd = (
        f"cd {mnt_task} && "
        f"MNT_OUTPUT_DIR={output_dir} "
        f"poetry run python main.py"
    )
    print(f"Running task...")
    manager.send_command(cmd, timeout=600)

    sys.exit(0)


if __name__ == "__main__":
    main()
