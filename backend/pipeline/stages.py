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

from . import rewrite, split
from .errors import StageError
from .parts import numbered_parts

# PIPELINE_MODEL overrides the model of every stage, including those that set their own.
MODEL_OVERRIDE = os.environ.get("PIPELINE_MODEL")
DEFAULT_MODEL = "haiku"

# The skill asks for at most 60 characters; this is the hard limit.
HEADLINE_MAX_CHARS = 70

IMAGE_LINK = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")


@dataclass(frozen=True)
class Stage:
    name: str
    # The skill in article-skills/ that the stage's agent runs.
    skill: str
    # Passed after the skill name. {article_id} is replaced with the folder name, and for
    # per-part stages {part} with the part's file name.
    args: str
    # Deleted before the stage runs, so a rerun never passes its check on stale files.
    outputs: tuple[str, ...]
    # Runs after the stage's agents and raises StageError if their output is unusable.
    check: Callable[[Path], None]
    # When true, a fresh agent runs for each part in parts/, in order, and check_part runs after
    # each one. A part that fails its check gets one more fresh agent.
    per_part: bool = False
    check_part: Callable[[Path, str], None] | None = None
    # Python that runs before the stage's agents, for example to prepare their input.
    prepare: Callable[[Path], None] | None = None
    # Python that runs after the agents and before check. It returns lines to print.
    finish: Callable[[Path], list[str]] | None = None
    tools: tuple[str, ...] = ("Read", "Write", "Glob", "Grep", "Skill")
    # None means DEFAULT_MODEL. A stage whose model is set in a config file uses model_setting
    # instead, which reads it from the article folder.
    model: str | None = None
    model_setting: Callable[[Path], str] | None = None
    # Seconds, for each agent.
    timeout: int = 10 * 60


def stage_model(stage: Stage, article: Path) -> str:
    if MODEL_OVERRIDE:
        return MODEL_OVERRIDE

    if stage.model_setting:
        return stage.model_setting(article)

    return stage.model or DEFAULT_MODEL


def check_metadata(article: Path) -> None:
    path = article / split.METADATA

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise StageError(f"{split.METADATA} was not created") from None
    except json.JSONDecodeError as exc:
        raise StageError(f"{split.METADATA} is not valid JSON: {exc}") from None

    if not isinstance(data, dict) or set(data) != {"authors", "affiliations", "topic"}:
        raise StageError(f'{split.METADATA} must have exactly the keys "authors", "affiliations" and "topic"')

    for key in ("authors", "affiliations"):
        values = data[key]

        if not isinstance(values, list) or not all(isinstance(value, str) and value.strip() for value in values):
            raise StageError(f'{split.METADATA} "{key}" must be a list of non-empty strings')

    if not data["authors"]:
        raise StageError(f'{split.METADATA} "authors" is empty')

    if not isinstance(data["topic"], str) or not data["topic"].strip():
        raise StageError(f'{split.METADATA} "topic" must be a non-empty string')


def check_abstract(article: Path) -> None:
    path = article / split.ABSTRACT

    if not path.is_file():
        raise StageError(f"{split.ABSTRACT} was not created")

    if not path.read_text(encoding="utf-8").strip():
        raise StageError(f"{split.ABSTRACT} is empty")


def check_split(article: Path) -> None:
    for part in numbered_parts(article / "parts"):
        for link in IMAGE_LINK.findall(part.read_text(encoding="utf-8")):
            if not re.match(r"[a-z]+://", link) and not (article / link).is_file():
                raise StageError(f"parts/{part.name} links to {link}, which doesn't exist")

    # Every block of the article must be in exactly one place (a part, dropped.md or the
    # back matter), copied byte for byte, with every kept graphic link as the parser wrote it.
    split.verify(article)
    check_metadata(article)
    check_abstract(article)


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

    abstract = article / split.ABSTRACT
    abstract_numbers = rewrite.numbers(abstract.read_text(encoding="utf-8")) if abstract.is_file() else set()
    seen: dict[str, str] = {}

    for part_id, titles in headers.items():
        if not isinstance(titles, list) or len(titles) != 3:
            raise StageError(f"headers.json {part_id} must have exactly 3 titles")

        # A headline may only use numbers that its own part or the abstract gives.
        allowed = abstract_numbers | rewrite.numbers((article / "rewritten" / f"{part_id}.md").read_text(encoding="utf-8"))

        for title in titles:
            if (
                not isinstance(title, dict)
                or set(title) != {"title"}
                or not isinstance(title["title"], str)
                or not title["title"].strip()
            ):
                raise StageError(f'headers.json {part_id} has an entry that isn\'t {{"title": "<text>"}}')

            text = title["title"].strip()

            if len(text) > HEADLINE_MAX_CHARS:
                raise StageError(
                    f"headers.json {part_id}: {text!r} has {len(text)} characters, more than {HEADLINE_MAX_CHARS}"
                )

            invented = sorted(rewrite.numbers(text) - allowed)

            if invented:
                raise StageError(f"headers.json {part_id}: {text!r} uses numbers that aren't in the part: {invented}")

            key = " ".join(text.casefold().rstrip(".!").split())

            if key in seen:
                raise StageError(f"headers.json repeats the headline {text!r} ({seen[key]} and {part_id})")

            seen[key] = part_id


STAGES = (
    # The agent decides where parts end and which blocks to delete, and writes the metadata.
    # Python measures reading time before it runs and cuts the text after, so the parts are
    # always exact copies of the blocks they keep.
    # Sonnet: choosing where a thought ends needs real reading comprehension, which Haiku got
    # wrong on the mocks, while the output is a short JSON plan, so Opus would add cost for little.
    Stage(
        name="split",
        skill="split-article",
        args=f"{split.ARTICLE} {split.OUTLINE} {split.PLAN} {split.METADATA} {split.ABSTRACT}",
        outputs=(
            "parts",
            split.OUTLINE,
            split.PLAN,
            split.BACK_MATTER,
            split.DROPPED,
            split.METADATA,
            split.ABSTRACT,
        ),
        check=check_split,
        prepare=split.write_outline,
        finish=split.apply_plan,
        model="sonnet",
    ),
    # A fresh agent per part keeps the context small. Each one reads the previous rewritten part
    # and a short shared notes file (terms, metaphors, tone), so the article keeps one style.
    # The style and the model come from rewrite-config.json. Python checks every part: graphics,
    # equations and captions unchanged, no number lost or added, and the length within range.
    Stage(
        name="rewrite",
        skill="rewrite-part",
        args=f"{rewrite.PARTS} {rewrite.REWRITTEN} {{part}} {rewrite.NOTES} {split.ABSTRACT} {rewrite.SETTINGS}",
        outputs=(rewrite.REWRITTEN, rewrite.NOTES, rewrite.SETTINGS),
        check=rewrite.check,
        per_part=True,
        check_part=rewrite.check_part,
        prepare=rewrite.prepare,
        finish=rewrite.report,
        tools=("Read", "Write", "Edit", "Glob", "Grep", "Skill"),
        model_setting=rewrite.configured_model,
    ),
    # One agent for the whole article, so the headlines can differ from part to part.
    # Sonnet: catchy but accurate needs both wit and reading comprehension, and the output is
    # short, so it costs little more than Haiku would.
    Stage(
        name="headlines",
        skill="write-headlines",
        args=f"rewritten headers.json {{article_id}} {split.ABSTRACT}",
        outputs=("headers.json",),
        check=check_headlines,
        model="sonnet",
        timeout=5 * 60,
    ),
)
