"""The LLM stages, in the order they run, and the checks on what each one writes.

Every path is relative to the article folder (output/<name>/), and so are the image links
inside the Markdown files: `images/x.png` means <article folder>/images/x.png.
"""

import json
import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MODEL = os.environ.get("PIPELINE_MODEL", "haiku")

PART_FILE = re.compile(r"part_(\d+)\.md")
IMAGE_LINK = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")


class StageError(Exception):
    pass


@dataclass(frozen=True)
class Stage:
    name: str
    # The skill in article-skills/ that the stage's agent runs.
    skill: str
    # Passed after the skill name. {article_id} is the folder name; {part} is the part's file name.
    args: str
    # Deleted before the stage runs, so a rerun never passes its check on stale files.
    outputs: tuple[str, ...]
    # Runs after the stage's agents and raises StageError if their output is unusable.
    check: Callable[[Path], None]
    # When set, one agent runs for each part_<n>.md in this folder, instead of one for the stage.
    parts_from: str | None = None
    tools: tuple[str, ...] = ("Read", "Write", "Glob", "Grep", "Skill")
    # None means DEFAULT_MODEL, which PIPELINE_MODEL can override.
    model: str | None = None
    # Seconds, per agent.
    timeout: int = 10 * 60


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


def check_split(article: Path) -> None:
    for part in numbered_parts(article / "parts"):
        for link in IMAGE_LINK.findall(part.read_text(encoding="utf-8")):
            if not re.match(r"[a-z]+://", link) and not (article / link).is_file():
                raise StageError(f"parts/{part.name} links to {link}, which doesn't exist")


def check_rewrite(article: Path) -> None:
    parts = [path.name for path in numbered_parts(article / "parts")]
    rewritten = [path.name for path in numbered_parts(article / "rewritten")]

    if rewritten != parts:
        raise StageError(f"rewritten/ has {len(rewritten)} parts, but parts/ has {len(parts)}")


def check_headlines(article: Path) -> None:
    path = article / "headers.json"
    expected = {part.stem for part in numbered_parts(article / "rewritten")}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise StageError("headers.json was not created") from None
    except json.JSONDecodeError as exc:
        raise StageError(f"headers.json is not valid JSON: {exc}") from None

    if not isinstance(data, dict) or set(data) != {"article_id", "headers"}:
        raise StageError('headers.json must have exactly the keys "article_id" and "headers"')

    if data["article_id"] != article.name:
        raise StageError(f'headers.json has article_id "{data["article_id"]}", expected "{article.name}"')

    headers = data["headers"]

    if not isinstance(headers, dict):
        raise StageError('"headers" in headers.json is not an object')

    if set(headers) != expected:
        missing = sorted(expected - set(headers))
        extra = sorted(set(headers) - expected)
        raise StageError(f"headers.json parts don't match rewritten/ (missing: {missing}, extra: {extra})")

    for part_id, titles in headers.items():
        if not isinstance(titles, list) or len(titles) != 3:
            raise StageError(f"headers.json {part_id} must have exactly 3 titles")

        for title in titles:
            if (
                not isinstance(title, dict)
                or set(title) != {"title"}
                or not isinstance(title["title"], str)
                or not title["title"].strip()
            ):
                raise StageError(f'headers.json {part_id} has an entry that isn\'t {{"title": "<text>"}}')


STAGES = (
    Stage(
        name="split",
        skill="split-article",
        args="article.md parts",
        outputs=("parts",),
        check=check_split,
    ),
    Stage(
        name="rewrite",
        skill="rewrite-part",
        args="parts/{part} rewritten/{part}",
        outputs=("rewritten",),
        check=check_rewrite,
        parts_from="parts",
        timeout=5 * 60,
    ),
    Stage(
        name="headlines",
        skill="write-headlines",
        args="rewritten headers.json {article_id}",
        outputs=("headers.json",),
        check=check_headlines,
        timeout=5 * 60,
    ),
)
