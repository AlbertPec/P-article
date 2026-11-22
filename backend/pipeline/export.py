"""The last stage, Python only: copies the finished article into the server's data folder.

data/articles/<article id>/ gets the layout from high-level-architecture-v2.md:

    images/                every image the parser extracted
    parts/                 the parts as split cut them
    particles/             the rewritten parts
    metadata.json
    original_article.pdf

panels.json isn't written yet. It pairs each headline with a panel image, and no stage makes
panel images yet, so the server's panels endpoint doesn't work for exported articles.

The server finds a particle's images by bare file name in images/, so image links `images/x.png`
become `x.png` in parts/ and particles/. Nothing else in the text changes. An earlier export of
the same article is replaced.
"""

import re
import shutil
import tempfile
from pathlib import Path

from p_article_server.storage import Storage, StorageError

from . import metadata, rewrite, split
from .errors import StageError
from .parse import BACKEND_DIR
from .parts import numbered_parts

DEFAULT_DATA_DIR = BACKEND_DIR / "data"
# The server's data folder. python -m pipeline sets it from --data-dir.
data_dir = DEFAULT_DATA_DIR

IMAGES = "images"
PARTICLES = "particles"
ORIGINAL_PDF = "original_article.pdf"

IMAGE_LINK_PREFIX = re.compile(r"(!\[[^\]]*\]\()images/")


def destination(article: Path) -> Path:
    return data_dir / "articles" / metadata.article_id(article)


def copy_parts(source: Path, target: Path) -> None:
    target.mkdir()

    for part in numbered_parts(source):
        # Bytes, not text, so line endings stay exactly as they are.
        text = part.read_bytes().decode("utf-8")
        (target / part.name).write_bytes(IMAGE_LINK_PREFIX.sub(r"\1", text).encode("utf-8"))


def original_pdf(article: Path) -> Path:
    # Parse copies the PDF into the article folder as <name>.pdf.
    pdfs = sorted(article.glob("*.pdf"))

    if len(pdfs) != 1:
        raise StageError(f"expected one PDF in {article.name}/, found {len(pdfs)}")

    return pdfs[0]


def export(article: Path) -> list[str]:
    """Writes data/articles/<article id>/. Returns lines to print."""

    pdf = original_pdf(article)
    target = destination(article)
    target.parent.mkdir(parents=True, exist_ok=True)

    # Build the folder under a hidden name, so a failed export leaves nothing the server would list.
    work = Path(tempfile.mkdtemp(dir=target.parent, prefix=".tmp-"))

    try:
        if (article / IMAGES).is_dir():
            shutil.copytree(article / IMAGES, work / IMAGES)
        else:
            (work / IMAGES).mkdir()

        copy_parts(article / rewrite.PARTS, work / rewrite.PARTS)
        copy_parts(article / rewrite.REWRITTEN, work / PARTICLES)
        shutil.copyfile(article / split.METADATA, work / split.METADATA)
        shutil.copyfile(pdf, work / ORIGINAL_PDF)

        if target.exists():
            shutil.rmtree(target)

        work.rename(target)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    return [f"exported to {target}"]


def check(article: Path) -> None:
    """Reads the export back the way the server does."""

    target = destination(article)
    article_id = target.name
    storage = Storage(data_dir)

    if article_id not in storage.article_ids():
        raise StageError(f"the server doesn't list {target}")

    count = len(numbered_parts(target / PARTICLES))

    try:
        meta = storage.read_metadata(article_id)

        for part_no in range(1, count + 1):
            storage.read_particle(article_id, part_no)
    except StorageError as exc:
        raise StageError(f"the server can't read {target}: {exc}") from None

    if meta.particle_count != count:
        raise StageError(f"{target.name}/{split.METADATA} says {meta.particle_count} particles, but there are {count}")
