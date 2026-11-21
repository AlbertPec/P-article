"""First step of the pipeline: turns a PDF into article.md and images/ with the existing parser."""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from fastapi import HTTPException

# Shared with the server, so both name output folders the same way.
from server import OUTPUT_DIR, PARSE_TIMEOUT_SECONDS, PARSER_SCRIPT, safe_stem, unique_folder


class ParseError(Exception):
    pass


def parse_pdf(pdf: Path) -> Path:
    """Parses pdf into a new folder in output/ and returns that folder."""

    if not pdf.is_file():
        raise ParseError(f"{pdf} does not exist")

    try:
        stem = safe_stem(pdf.name)
    except HTTPException as exc:
        raise ParseError(exc.detail) from None

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
