"""The Python half of the split stage.

The agent makes the decisions; this module does everything that needs exact counting or copying:

- Before the agent runs, write_outline() numbers the article's blocks (paragraphs, headings,
  graphics) and writes split-outline.md with each block's lines and reading time.
- After it runs, apply_plan() reads the agent's split-plan.json and cuts article.md along it:
  each part gets its blocks byte for byte, minus the blocks the plan drops (journal headers,
  logos and other page furniture), which go to dropped.md so every deletion can be reviewed.
  Nothing is retyped, so every kept graphic link stays exactly as it is in article.md.
"""

import json
import re
import struct
from dataclasses import dataclass
from pathlib import Path

from .errors import StageError

ARTICLE = "article.md"
OUTLINE = "split-outline.md"
PLAN = "split-plan.json"
BACK_MATTER = "back-matter.md"
DROPPED = "dropped.md"
METADATA = "metadata.json"
# The abstract as plain text: kept out of the parts, and given to later stages as context.
ABSTRACT = "abstract.md"

# Adults read non-fiction at roughly 240 words per minute; technical text is a little slower.
WORDS_PER_MINUTE = 230
# Equations and tables are graphics in article.md, and they take a moment to read too.
SECONDS_PER_GRAPHIC = 10
TARGET_MINUTES = (4, 5)

GRAPHIC = re.compile(r"!\[[^\]]*\]\(([^)]*)\)")
WORD = re.compile(r"[^\W_]+")
PICTURE_TEXT = "<!-- Start of picture text -->"
# Blocks a part shouldn't start or end with.
GRAPHIC_KINDS = ("graphic", "pic-text")


@dataclass(frozen=True)
class Block:
    number: int
    # 1-based and inclusive, as Read shows them.
    first_line: int
    last_line: int
    kind: str  # "heading", "graphic", "pic-text" or "text"
    words: int
    graphics: int
    preview: str

    @property
    def seconds(self) -> float:
        return self.words / WORDS_PER_MINUTE * 60 + self.graphics * SECONDS_PER_GRAPHIC


@dataclass(frozen=True)
class Plan:
    # Each part's first and last block, in order.
    parts: list[tuple[int, int]]
    back_matter: int | None
    # Block number -> why it's deleted.
    drop: dict[int, str]


def read_lines(article: Path) -> list[str]:
    return (article / ARTICLE).read_text(encoding="utf-8").splitlines(keepends=True)


def png_size(path: Path) -> str:
    """Returns a PNG's size as "150x164px", or "" if it can't be read."""

    try:
        with path.open("rb") as file:
            header = file.read(24)
    except OSError:
        return ""

    if header[:8] != b"\x89PNG\r\n\x1a\n":
        return ""

    width, height = struct.unpack(">II", header[16:24])

    return f"{width}x{height}px"


def parse_blocks(lines: list[str], article: Path | None = None) -> list[Block]:
    """Splits the article into blocks: runs of non-blank lines, as the parser separates them."""

    blocks = []
    start = None

    for number, line in enumerate([*lines, ""], 1):
        if line.strip():
            if start is None:
                start = number
        elif start is not None:
            blocks.append(make_block(len(blocks) + 1, start, number - 1, lines[start - 1:number - 1], article))
            start = None

    return blocks


def make_block(number: int, first_line: int, last_line: int, lines: list[str], article: Path | None) -> Block:
    body = "".join(lines).strip()
    links = GRAPHIC.findall(body)
    text = " ".join(GRAPHIC.sub(" ", body).split())

    if links and not text.strip(" *_"):
        kind = "graphic"
        size = png_size(article / links[0]) if article else ""
        preview = GRAPHIC.search(body)[0] + (f" {size}" if size else "")
        preview += f" (+{len(links) - 1} more)" if len(links) > 1 else ""
    elif body.startswith(PICTURE_TEXT):
        # The parser's text version of the graphic just before it, usually an equation.
        kind = "pic-text"
        preview = " ".join(re.sub(r"<!--.*?-->|<br>", " ", body).split())[:70]
    elif len(lines) == 1 and body.startswith("#"):
        kind = "heading"
        preview = body
    else:
        kind = "text"
        preview = text[:70] + ("…" if len(text) > 70 else "")

    return Block(number, first_line, last_line, kind, len(WORD.findall(text)), len(links), preview)


def clock(seconds: float) -> str:
    return f"{int(seconds // 60)}:{int(seconds % 60):02d}"


def write_outline(article: Path) -> None:
    blocks = parse_blocks(read_lines(article), article)

    if not blocks:
        raise StageError(f"{ARTICLE} is empty")

    total = sum(block.seconds for block in blocks)
    rows = []
    elapsed = 0.0

    for block in blocks:
        elapsed += block.seconds
        lines = f"L{block.first_line}-{block.last_line}"
        rows.append(
            f"B{block.number:<4} {lines:<10} {block.kind:<8} "
            f"{block.words:>4}w {block.graphics:>2}g {block.seconds:>5.0f}s  {clock(elapsed):>6}  {block.preview}"
        )

    header = [
        f"# Outline of {ARTICLE}",
        "",
        f"{len(blocks)} blocks, {clock(total)} of reading in total. Reading time is {WORDS_PER_MINUTE} words "
        f"per minute plus {SECONDS_PER_GRAPHIC} seconds per graphic.",
        "",
        "Columns: block, lines in article.md, kind, words, graphics, reading seconds, reading time "
        "from the start of the article to the end of this block, preview. Kind pic-text is the "
        "parser's text version of the graphic just before it. Graphic previews show the image's size.",
        "",
    ]

    (article / OUTLINE).write_text("\n".join(header + rows) + "\n", encoding="utf-8")


def load_plan(article: Path, block_count: int) -> Plan:
    try:
        plan = json.loads((article / PLAN).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise StageError(f"{PLAN} was not created") from None
    except json.JSONDecodeError as exc:
        raise StageError(f"{PLAN} is not valid JSON: {exc}") from None

    if not isinstance(plan, dict) or not isinstance(plan.get("parts"), list) or not plan["parts"]:
        raise StageError(f'{PLAN} must be an object with a non-empty "parts" list')

    ranges = []

    for number, part in enumerate(plan["parts"], 1):
        first = part.get("first_block") if isinstance(part, dict) else None
        last = part.get("last_block") if isinstance(part, dict) else None

        if not isinstance(first, int) or not isinstance(last, int):
            raise StageError(f'{PLAN} part {number} needs whole-number "first_block" and "last_block"')

        if first > last:
            raise StageError(f"{PLAN} part {number} ends (B{last}) before it starts (B{first})")

        expected = ranges[-1][1] + 1 if ranges else 1

        if first != expected:
            raise StageError(f"{PLAN} part {number} starts at B{first}, but must start at B{expected}")

        ranges.append((first, last))

    back_matter = plan.get("back_matter_first_block")
    end = ranges[-1][1]

    if back_matter is None:
        if end != block_count:
            raise StageError(f"{PLAN} parts end at B{end}, but the article has {block_count} blocks")
    elif not isinstance(back_matter, int) or back_matter != end + 1 or back_matter > block_count:
        raise StageError(f'{PLAN} "back_matter_first_block" must be B{end + 1}, right after the last part')

    drop = {}

    for entry in plan.get("drop") or []:
        block = entry.get("block") if isinstance(entry, dict) else None
        reason = entry.get("reason") if isinstance(entry, dict) else None

        if not isinstance(block, int) or not isinstance(reason, str) or not reason.strip():
            raise StageError(f'{PLAN} "drop" entries need a whole-number "block" and a "reason"')

        if not 1 <= block <= end:
            raise StageError(f"{PLAN} drops B{block}, which isn't in any part")

        if block in drop:
            raise StageError(f"{PLAN} drops B{block} twice")

        drop[block] = reason.strip()

    for number, (first, last) in enumerate(ranges, 1):
        if all(block in drop for block in range(first, last + 1)):
            raise StageError(f"{PLAN} drops every block of part {number}")

    return Plan(ranges, back_matter, drop)


def move_trailing_headings(plan: Plan, blocks: list[Block]) -> tuple[Plan, list[str]]:
    """Moves headings that end a part to the start of the next part, where they belong.

    A heading always introduces the text after it, so this fix is never a judgement call.
    """

    parts = [list(part) for part in plan.parts]
    notes = []

    for index in range(len(parts) - 1):
        while True:
            first, last = parts[index]
            kept = [number for number in range(first, last + 1) if number not in plan.drop]

            if not kept:
                raise StageError(f"part {index + 1} has no blocks left after moving its headings to the next part")

            if blocks[kept[-1] - 1].kind != "heading":
                break

            parts[index][1] = kept[-1] - 1
            parts[index + 1][0] = kept[-1]
            notes.append(f"moved heading B{kept[-1]} from the end of part_{index + 1} to the start of part_{index + 2}")

    return Plan([(first, last) for first, last in parts], plan.back_matter, plan.drop), notes


def build_outputs(article: Path) -> tuple[dict[str, str], list[str]]:
    """Works out every file the plan produces, and a report line per part plus any warnings."""

    lines = read_lines(article)
    blocks = parse_blocks(lines)
    plan, fixes = move_trailing_headings(load_plan(article, len(blocks)), blocks)

    # Each block owns its lines plus the blank lines after it; the first block also owns any
    # blank lines at the top. So the blocks' segments, in order, are exactly article.md.
    starts = [1] + [block.first_line for block in blocks[1:]]
    ends = [start - 1 for start in starts[1:]] + [len(lines)]
    segments = ["".join(lines[start - 1:end]) for start, end in zip(starts, ends)]

    if "".join(segments) != "".join(lines):
        raise StageError(f"internal error: the blocks don't cover {ARTICLE} exactly")

    outputs = {}
    report = [f"fixed: {fix}" for fix in fixes]
    dropped = []
    low, high = TARGET_MINUTES

    for number, (first, last) in enumerate(plan.parts, 1):
        kept = [block for block in blocks[first - 1:last] if block.number not in plan.drop]
        outputs[f"parts/part_{number}.md"] = "".join(segments[block.number - 1] for block in kept)

        for block in blocks[first - 1:last]:
            if block.number in plan.drop:
                dropped.append(
                    f"<!-- B{block.number}, lines {block.first_line}-{block.last_line}, from part_{number}: "
                    f"{plan.drop[block.number]} -->\n{segments[block.number - 1]}"
                )

        minutes = sum(block.seconds for block in kept) / 60
        content = [block for block in kept if block.kind != "heading"]
        report.append(
            f"part_{number}: B{first}-B{last}, {minutes:.1f} min, {sum(block.words for block in kept)} words, "
            f"{sum(block.graphics for block in kept)} graphics, {last - first + 1 - len(kept)} blocks dropped"
        )

        if not low <= minutes <= high:
            report.append(f"  warning: part_{number} is {minutes:.1f} min, outside {low}-{high}")

        if content and content[0].kind in GRAPHIC_KINDS:
            report.append(f"  warning: part_{number} starts with a graphic (B{content[0].number})")

        if kept[-1].kind in GRAPHIC_KINDS:
            report.append(f"  warning: part_{number} ends with a graphic (B{kept[-1].number})")

        if kept[-1].kind == "heading":
            report.append(f"  warning: part_{number} ends with a heading (B{kept[-1].number})")

    if dropped:
        outputs[DROPPED] = "".join(dropped)
        report.append(f"{DROPPED}: {len(dropped)} blocks deleted from the parts")

    if plan.back_matter:
        outputs[BACK_MATTER] = "".join(segments[plan.back_matter - 1:])
        report.append(f"{BACK_MATTER}: B{plan.back_matter}-B{len(blocks)}, left out of the parts")

    return outputs, report


def apply_plan(article: Path) -> list[str]:
    """Cuts article.md along split-plan.json. Returns a line per part, plus any warnings."""

    outputs, report = build_outputs(article)
    (article / "parts").mkdir()

    for path, text in outputs.items():
        (article / path).write_text(text, encoding="utf-8")

    return report


def verify(article: Path) -> None:
    """Raises unless the files on disk are exactly what the plan produces from article.md."""

    outputs, _ = build_outputs(article)

    for path, text in outputs.items():
        file = article / path

        if not file.is_file() or file.read_text(encoding="utf-8") != text:
            raise StageError(f"{path} isn't exactly what {PLAN} cuts from {ARTICLE}")

    for path in (BACK_MATTER, DROPPED):
        if path not in outputs and (article / path).exists():
            raise StageError(f"{path} exists, but {PLAN} doesn't produce it")
