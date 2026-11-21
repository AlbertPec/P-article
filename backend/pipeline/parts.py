"""The numbered part files that split writes and later stages read."""

import re
from pathlib import Path

from .errors import StageError

PART_FILE = re.compile(r"part_(\d+)\.md")


def numbered_parts(folder: Path) -> list[Path]:
    """Returns part_1.md … part_N.md in order, or raises if any are missing, extra or empty."""

    if not folder.is_dir():
        raise StageError(f"{folder.name}/ was not created")

    parts = {}

    for path in folder.iterdir():
        if path.name.startswith("."):
            continue

        match = PART_FILE.fullmatch(path.name)

        if not match:
            raise StageError(f"unexpected file {folder.name}/{path.name}")

        parts[int(match[1])] = path

    if not parts:
        raise StageError(f"{folder.name}/ is empty")

    if sorted(parts) != list(range(1, len(parts) + 1)):
        raise StageError(f"{folder.name}/ is not numbered part_1.md to part_{len(parts)}.md")

    for path in parts.values():
        if not path.read_text(encoding="utf-8").strip():
            raise StageError(f"{folder.name}/{path.name} is empty")

    return [parts[number] for number in sorted(parts)]
