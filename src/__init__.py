from __future__ import annotations

import sys


def log(*args: object) -> None:
    print(*args, file=sys.stderr)
