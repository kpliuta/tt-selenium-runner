from __future__ import annotations

import os
import shlex
import sys
from pathlib import Path
from typing import Mapping

from src import log
from src.proot_manager import ProotManager


def build_env_prefix(
    env: Mapping[str, str],
    extra: Mapping[str, str] | None = None,
) -> str:
    """Build a shell env-assignment prefix for VAR_* and extra env vars.

    Runner and task parameters reach task_exec.py as VAR_* env vars. Values
    are shell-quoted so the prefix stays safe when a value contains spaces
    or other special characters. Returns an empty string when there are no
    vars to set.
    """
    assignments: dict[str, str] = {}
    if extra:
        assignments.update(
            {key: shlex.quote(value) for key, value in extra.items()}
        )
    assignments.update(
        {
            key: shlex.quote(value)
            for key, value in env.items()
            if key.startswith("VAR_")
        }
    )
    return " ".join(f"{key}={value}" for key, value in assignments.items())


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
    manager.send_command(f"cd {shlex.quote(mnt_task)}", 10)
    env_prefix = build_env_prefix(os.environ, extra={"MNT_OUTPUT_DIR": output_dir})
    task_command = (
        f"{env_prefix} poetry run python src/main.py"
        if env_prefix else
        "poetry run python src/main.py"
    )
    manager.send_command(task_command, timeout=600)

    sys.exit(0)


if __name__ == "__main__":
    main()
