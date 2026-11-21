"""First step of the pipeline: turns a PDF into article.md and images/ with the parser, pdf_to_md.py."""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
PARSER_SCRIPT = BACKEND_DIR / "pdf_to_md.py"
# The pipeline's working folders, one per article. They are not what the server reads.
OUTPUT_DIR = BACKEND_DIR / "output"
PARSE_TIMEOUT_SECONDS = 10 * 60


class ParseError(Exception):
    pass


def safe_stem(filename: str) -> str:
    """Reduces a PDF's file name to a stem that is safe to use as a folder name."""

    name = filename.replace("\\", "/").rsplit("/", 1)[-1]

    if not name.lower().endswith(".pdf"):
        raise ParseError(f"{filename} is not a .pdf file")

    # No spaces: PyMuPDF4LLM swaps them for underscores in image paths, and the parse then fails.
    stem = re.sub(r"[^\w.-]+", "_", name[:-4]).strip("_.-")

    return stem[:100] or "article"


def unique_folder(stem: str) -> Path:
    """Returns an unused output folder, so parsing a file again never overwrites a result."""

    folder = OUTPUT_DIR / stem
    suffix = 2

    while folder.exists():
        folder = OUTPUT_DIR / f"{stem}-{suffix}"
        suffix += 1

    return folder


def parse_pdf(pdf: Path) -> Path:
    """Parses pdf into a new folder in output/ and returns that folder."""

    if not pdf.is_file():
        raise ParseError(f"{pdf} does not exist")

    stem = safe_stem(pdf.name)
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Work in a hidden folder so a failed parse leaves nothing behind in output/.
    work_dir = Path(tempfile.mkdtemp(dir=OUTPUT_DIR, prefix=".tmp-"))

    try:
        copy = work_dir / f"{stem}.pdf"
        shutil.copyfile(pdf, copy)

        try:
            # Output isn't captured, so the parser's progress shows in the terminal.
            result = subprocess.run(
                [sys.executable, str(PARSER_SCRIPT), str(copy)],
                cwd=work_dir,
                timeout=PARSE_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            raise ParseError("parsing took too long") from None

        if result.returncode != 0:
            raise ParseError("the parser could not read this PDF (its output is above)")

        folder = unique_folder(stem)
        shutil.move(work_dir / stem, folder)

        return folder

    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
