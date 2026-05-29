from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.proot_manager import ProotManager


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python after_exec.py <runner_path>", file=sys.stderr)
        sys.exit(1)

    runner_path = Path(sys.argv[1])
    manager = ProotManager(runner_path)

    if not manager.in_fifo.exists():
        print("No active proot session to shut down.")
        sys.exit(0)

    print("Shutting down proot session...")
    manager.stop_proot(timeout=60)
    print("Proot session shut down.")
    sys.exit(0)


if __name__ == "__main__":
    main()
