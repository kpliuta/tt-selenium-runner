from __future__ import annotations

import sys
from pathlib import Path

from src import log
from src.proot_manager import ProotManager


def main() -> None:
    if len(sys.argv) < 2:
        log("Usage: python -m src.after_exec <runner_path>")
        sys.exit(1)

    runner_path = Path(sys.argv[1])
    manager = ProotManager(runner_path)

    if not manager.in_fifo.exists():
        log("No active proot session to shut down.")
        sys.exit(0)

    log("Shutting down proot session...")
    manager.stop_proot(timeout=60)
    log("Proot session shut down.")
    sys.exit(0)


if __name__ == "__main__":
    main()
