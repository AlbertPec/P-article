"""The Python half of the rewrite stage.

The agents rewrite the text; this module makes sure they only changed how it reads:

- Before the agents run, prepare() reads the style settings and writes rewrite-settings.json,
  with each part's word budget, for the agents to read.
- After each part, check_part() compares the rewritten part with the original. Graphics, the
  parser's text versions of equations, and captions must be copied byte for byte and in the same
  order. Every number in the original text must still be there, no new number may appear, and
  the length must stay within the configured range.

The original parts in parts/ are never changed: the rewrites go to rewritten/, and the check
fails if parts/ no longer matches what split cut from article.md.
"""

import json
import re
from pathlib import Path

from . import split
from .errors import StageError
from .parts import numbered_parts

PARTS = "parts"
REWRITTEN = "rewritten"
NOTES = "rewrite-notes.md"
NOTES_LIMIT = 8000

# The default style. An article folder can hold its own rewrite-config.json with only the keys
# it changes; prepare() merges the two and writes the result to SETTINGS for the agents.
DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "rewrite-config.json"
ARTICLE_CONFIG = "rewrite-config.json"
SETTINGS = "rewrite-settings.json"

# The allowed values of each setting. The skill (article-skills/skills/rewrite-part/SKILL.md)
# says what each value means, so a new value must be added in both places.
CHOICES = {
    "style": ("formal", "neutral", "friendly", "catchy"),
    "explanation": ("none", "light", "moderate", "thorough"),
    "metaphors": ("none", "occasional", "frequent"),
    "sentences": ("as_original", "shorter", "short_and_simple"),
}
# "model" is the Claude model that rewrites, such as "sonnet", "opus" or "haiku". PIPELINE_MODEL overrides it.
TEXT_SETTINGS = ("model", "audience", "language", "extra_instructions")
LENGTH_LIMITS = (0.5, 2.0)
# Parts with less text than this don't get a length check, because a few words change the ratio a lot.
MIN_WORDS_FOR_RATIO = 60

CAPTION = re.compile(r"\*\*(?:Fig(?:ure)?\.?|Table|Scheme|Algorithm)\s*\d+", re.IGNORECASE)
TABLE_LABEL = re.compile(r"\*\*Table\s*\d+\.?\*\*", re.IGNORECASE)
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
LIST_MARKER = re.compile(r"^\s*\d+[.)]\s", re.MULTILINE)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
SUP_SUB_TAG = re.compile(r"</?(?:sup|sub)>", re.IGNORECASE)
SCRIPT_DIGITS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉", "01234567890123456789")


def load_config(article: Path) -> dict:
    """Returns the default style merged with the article's own rewrite-config.json, if it has one."""

    config = read_json(DEFAULT_CONFIG)
    override_path = article / ARTICLE_CONFIG

    if override_path.is_file():
        override = read_json(override_path)

        if not isinstance(override, dict):
            raise StageError(f"{override_path} must be a JSON object")

        for key, value in override.items():
            if key == "length" and isinstance(value, dict) and isinstance(config.get("length"), dict):
                config["length"] = {**config["length"], **value}
            else:
                config[key] = value

    validate_config(config)

    return config


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise StageError(f"{path} doesn't exist") from None
    except json.JSONDecodeError as exc:
        raise StageError(f"{path} is not valid JSON: {exc}") from None


def validate_config(config) -> None:
    if not isinstance(config, dict):
        raise StageError("the rewrite config must be a JSON object")

    expected = {*CHOICES, *TEXT_SETTINGS, "length"}
    unknown = sorted(set(config) - expected)
    missing = sorted(expected - set(config))

    if unknown:
        raise StageError(f"unknown rewrite settings: {unknown}. Allowed: {sorted(expected)}")

    if missing:
        raise StageError(f"missing rewrite settings: {missing}")

    for key, choices in CHOICES.items():
        if config[key] not in choices:
            raise StageError(f'rewrite setting "{key}" is {config[key]!r}, but must be one of {list(choices)}')

    for key in TEXT_SETTINGS:
        if not isinstance(config[key], str):
            raise StageError(f'rewrite setting "{key}" must be a string')

    for key in ("model", "audience", "language"):
        if not config[key].strip():
            raise StageError(f'rewrite setting "{key}" is empty')

    length = config["length"]
    low, high = LENGTH_LIMITS

    if not isinstance(length, dict) or set(length) != {"min_ratio", "max_ratio"}:
        raise StageError('rewrite setting "length" must be {"min_ratio": <number>, "max_ratio": <number>}')

    if not all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in length.values()):
        raise StageError('rewrite setting "length" must hold numbers')

    if not low <= length["min_ratio"] <= 1 <= length["max_ratio"] <= high:
        raise StageError(
            f'rewrite setting "length" must have {low} <= min_ratio <= 1 <= max_ratio <= {high}, '
            f"got {length['min_ratio']} and {length['max_ratio']}"
        )


def configured_model(article: Path) -> str:
    return load_config(article)["model"]


def split_blocks(text: str) -> list[tuple[str, str]]:
    """Returns each block of a part as (kind, text), where kind is "protected" or "text".

    Protected blocks are graphics, the parser's text versions of them (pic-text) and captions,
    including a table's title after its "**Table N**" label. They must be copied unchanged.
    """

    lines = text.splitlines(keepends=True)
    result = []
    previous = ""

    for block in split.parse_blocks(lines):
        body = "".join(lines[block.first_line - 1:block.last_line]).strip()
        protected = (
            block.kind in split.GRAPHIC_KINDS
            or CAPTION.match(body) is not None
            or (TABLE_LABEL.fullmatch(previous) is not None and block.kind == "text")
        )
        result.append(("protected" if protected else "text", body))
        previous = body

    return result


def plain(text: str) -> str:
    """The text with graphic links, comments and <sup>/<sub> tags removed, for counting."""

    text = split.GRAPHIC.sub(" ", text)
    text = HTML_COMMENT.sub(" ", text)
    text = SUP_SUB_TAG.sub("", text)

    return text.translate(SCRIPT_DIGITS)


def numbers(text: str) -> set[str]:
    """Every number in the text, with a decimal comma read as a point. List markers don't count."""

    return {match.replace(",", ".") for match in NUMBER.findall(LIST_MARKER.sub(" ", plain(text)))}


def text_of(blocks: list[tuple[str, str]]) -> str:
    return "\n\n".join(body for kind, body in blocks if kind == "text")


def words(text: str) -> int:
    return len(split.WORD.findall(plain(text)))


def word_budget(original_words: int, config: dict) -> dict:
    length = config["length"]

    return {
        "original_words": original_words,
        "min_words": round(original_words * length["min_ratio"]),
        "max_words": round(original_words * length["max_ratio"]),
    }


def prepare(article: Path) -> None:
    config = load_config(article)
    budgets = {}

    for part in numbered_parts(article / PARTS):
        budgets[part.name] = word_budget(words(text_of(split_blocks(part.read_text(encoding="utf-8")))), config)

    settings = {**config, "word_budget": budgets}
    (article / SETTINGS).write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check_notes(article: Path) -> None:
    path = article / NOTES

    if not path.is_file():
        raise StageError(f"{NOTES} was not created")

    notes = path.read_text(encoding="utf-8")

    if not notes.strip():
        raise StageError(f"{NOTES} is empty")

    # The notes are the only memory passed from part to part, so they mustn't become a second
    # context that grows with the article.
    if len(notes) > NOTES_LIMIT:
        raise StageError(f"{NOTES} has {len(notes)} characters, more than the {NOTES_LIMIT} allowed")


def short(text: str, limit: int = 80) -> str:
    text = " ".join(text.split())

    return text if len(text) <= limit else text[:limit] + "…"


def compare(article: Path, part: str) -> tuple[int, int]:
    """Raises if rewritten/<part> changed anything but the wording. Returns the word counts."""

    path = article / REWRITTEN / part

    if not path.is_file():
        raise StageError(f"{REWRITTEN}/{part} was not created")

    rewritten_text = path.read_text(encoding="utf-8")

    if not rewritten_text.strip():
        raise StageError(f"{REWRITTEN}/{part} is empty")

    original = split_blocks((article / PARTS / part).read_text(encoding="utf-8"))
    rewritten = split_blocks(rewritten_text)
    problems = []

    # Graphics, equations and captions: the same blocks, byte for byte, in the same order.
    kept = [body for kind, body in original if kind == "protected"]
    found = [body for kind, body in rewritten if kind == "protected"]

    if found != kept:
        for index, body in enumerate(kept):
            if index >= len(found) or found[index] != body:
                problems.append(
                    f"graphic/caption block {index + 1} of {len(kept)} must be copied unchanged as its own block "
                    f"and in its original order: {short(body)!r}"
                )
                break
        else:
            problems.append(f"there are {len(found) - len(kept)} extra graphic/caption blocks: {short(found[len(kept)])!r}")

    # Every graphic link, wherever it is.
    if split.GRAPHIC.findall(rewritten_text) != split.GRAPHIC.findall((article / PARTS / part).read_text(encoding="utf-8")):
        problems.append("the image links are not exactly the original ones in the original order")

    # Numbers: none lost, none invented.
    original_text, new_text = text_of(original), text_of(rewritten)
    allowed = numbers("\n\n".join(body for _, body in original))
    abstract = article / split.ABSTRACT

    if abstract.is_file():
        allowed |= numbers(abstract.read_text(encoding="utf-8"))

    missing = sorted(numbers(original_text) - numbers(new_text))
    added = sorted(numbers(new_text) - allowed)

    if missing:
        problems.append(f"numbers from the original are missing, keep them exactly as written: {missing[:15]}")

    if added:
        problems.append(f"numbers that aren't in the original part or the abstract were added: {added[:15]}")

    # Length.
    before, after = words(original_text), words(new_text)

    if before >= MIN_WORDS_FOR_RATIO:
        budget = word_budget(before, load_config(article))

        if not budget["min_words"] <= after <= budget["max_words"]:
            problems.append(
                f"the text has {after} words, but must have {budget['min_words']}-{budget['max_words']} "
                f"(the original has {before})"
            )

    if problems:
        raise StageError(f"{REWRITTEN}/{part}: " + "; ".join(problems))

    return before, after


def check_part(article: Path, part: str) -> None:
    compare(article, part)
    check_notes(article)
    # The originals must stay exactly as split cut them.
    split.verify(article)


def check(article: Path) -> None:
    parts = [path.name for path in numbered_parts(article / PARTS)]
    rewritten = [path.name for path in numbered_parts(article / REWRITTEN)]

    if rewritten != parts:
        raise StageError(f"{REWRITTEN}/ has {len(rewritten)} parts, but {PARTS}/ has {len(parts)}")

    for part in parts:
        compare(article, part)

    check_notes(article)
    split.verify(article)


def report(article: Path) -> list[str]:
    lines = []

    for part in numbered_parts(article / REWRITTEN):
        before, after = compare(article, part.name)
        ratio = after / before if before else 1
        lines.append(f"{part.stem}: {before} -> {after} words ({ratio:.2f}x)")

    return lines
