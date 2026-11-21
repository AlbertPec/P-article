"""The article's id, and the stage that completes metadata.json with it and the particle count.

The id is the article_id from high-level-architecture-v2.md, a UUIDv4. It's created the first
time the pipeline runs on an article folder and saved in article-id.txt, which no stage clears,
so every rerun, including a rerun of split, keeps the same id. Headlines write it into
headers.json, and export names the article's folder in data/ with it.

Split's agent writes the title, authors, affiliations and topic. The metadata stage, Python only,
adds:

- "id": the article's id
- "particle_count": the number of rewritten parts, which become the article's particles
"""

import json
import uuid
from pathlib import Path

from . import rewrite, split
from .errors import StageError
from .parts import numbered_parts

ID_FILE = "article-id.txt"

ID = "id"
PARTICLE_COUNT = "particle_count"
# What split's agent writes.
SPLIT_KEYS = ("title", "authors", "affiliations", "topic")
# The final metadata.json, in the order of the architecture's GET /articles/{article_id}.
FINAL_KEYS = (ID, *SPLIT_KEYS, PARTICLE_COUNT)


def is_uuid4(value) -> bool:
    if not isinstance(value, str):
        return False

    try:
        parsed = uuid.UUID(value)
    except ValueError:
        return False

    return parsed.version == 4 and str(parsed) == value


def article_id(article: Path) -> str:
    """Returns the article's id, creating it on first use."""

    path = article / ID_FILE

    if path.is_file():
        value = path.read_text(encoding="utf-8").strip()

        if not is_uuid4(value):
            raise StageError(f"{ID_FILE} must hold a UUIDv4, got {value!r}")

        return value

    value = str(uuid.uuid4())
    path.write_text(value + "\n", encoding="utf-8")

    return value


def particle_count(article: Path) -> int:
    return len(numbered_parts(article / rewrite.REWRITTEN))


def complete(article: Path) -> list[str]:
    """Writes the id and particle count into metadata.json. Returns lines to print."""

    path = article / split.METADATA

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise StageError(f"{split.METADATA} doesn't exist; run split first") from None
    except json.JSONDecodeError as exc:
        raise StageError(f"{split.METADATA} is not valid JSON: {exc}") from None

    if not isinstance(data, dict):
        raise StageError(f"{split.METADATA} is not a JSON object")

    data |= {ID: article_id(article), PARTICLE_COUNT: particle_count(article)}
    # The keys the order lists first, then anything else, which the check will reject.
    ordered = {key: data[key] for key in FINAL_KEYS if key in data}
    ordered |= {key: value for key, value in data.items() if key not in ordered}

    path.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return [f"{ID} {data[ID]}, {PARTICLE_COUNT} {data[PARTICLE_COUNT]}"]
