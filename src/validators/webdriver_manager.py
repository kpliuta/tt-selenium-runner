from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python src/validators/webdriver_manager.py <task_path>", file=sys.stderr)
        sys.exit(1)

    task_path = Path(sys.argv[1])
    pyproject = task_path / "pyproject.toml"

    if not pyproject.exists():
        print("pyproject.toml not found", file=sys.stderr)
        sys.exit(1)

    content = pyproject.read_text()

    dep_patterns = [
        re.compile(r'^webdriver-manager\s*[>=<]', re.MULTILINE),
        re.compile(r'"webdriver-manager\s*[>=<]', re.MULTILINE),
        re.compile(r"'webdriver-manager\s*[>=<]", re.MULTILINE),
    ]

    for pattern in dep_patterns:
        if pattern.search(content):
            sys.exit(0)

    print("webdriver-manager dependency not found in pyproject.toml", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
