import asyncio
import logging
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.concurrency import run_in_threadpool

BACKEND_DIR = Path(__file__).resolve().parent
PARSER_SCRIPT = BACKEND_DIR / "pdf_to_md_v2.py"
OUTPUT_DIR = BACKEND_DIR / "output"

MAX_UPLOAD_BYTES = 200 * 1024 * 1024
PARSE_TIMEOUT_SECONDS = 10 * 60

logger = logging.getLogger("uvicorn.error")
app = FastAPI(title="P-article parser")

# Only one PDF is parsed at a time, in the order the uploads arrive.
parse_lock = asyncio.Lock()


def safe_stem(filename: str) -> str:
    """Reduces a client-supplied filename to a stem that is safe to use as a folder name."""

    name = filename.replace("\\", "/").rsplit("/", 1)[-1]

    if not name.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only .pdf files can be parsed")

    # No spaces: PyMuPDF4LLM swaps them for underscores in image paths, and the parse then fails.
    stem = re.sub(r"[^\w.-]+", "_", name[:-4]).strip("_.")

    return stem[:100] or "article"


def unique_folder(stem: str) -> Path:
    """Returns an unused output folder, so parsing a file again never overwrites a result."""

    folder = OUTPUT_DIR / stem
    suffix = 2

    while folder.exists():
        folder = OUTPUT_DIR / f"{stem}-{suffix}"
        suffix += 1

    return folder


async def save_upload(request: Request, target: Path) -> None:
    """Streams the request body to disk, rejecting anything that isn't a PDF of a sane size."""

    size = 0

    with target.open("wb") as file:
        async for chunk in request.stream():
            if size == 0 and not chunk:
                continue

            if size == 0 and not chunk.startswith(b"%PDF-"):
                raise HTTPException(status_code=400, detail="The file is not a valid PDF")

            size += len(chunk)

            if size > MAX_UPLOAD_BYTES:
                raise HTTPException(status_code=413, detail="The file is too large")

            file.write(chunk)

    if size == 0:
        raise HTTPException(status_code=400, detail="The file is empty")


def run_parser(pdf: Path) -> None:
    """Runs the parser in its own process, so a crash can't take the server down."""

    try:
        result = subprocess.run(
            [sys.executable, str(PARSER_SCRIPT), str(pdf)],
            cwd=pdf.parent,
            capture_output=True,
            text=True,
            timeout=PARSE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        logger.error("Parsing %s timed out", pdf.name)
        raise HTTPException(status_code=504, detail="Parsing took too long")

    if result.returncode != 0:
        logger.error("Parsing %s failed:\n%s\n%s", pdf.name, result.stdout, result.stderr)
        raise HTTPException(status_code=422, detail="The parser could not read this PDF")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/articles")
async def parse_article(request: Request, filename: str = Query(min_length=1)) -> dict:
    stem = safe_stem(filename)

    OUTPUT_DIR.mkdir(exist_ok=True)

    # Work in a hidden folder so a failed parse leaves nothing behind in output/.
    work_dir = Path(tempfile.mkdtemp(dir=OUTPUT_DIR, prefix=".tmp-"))

    try:
        pdf = work_dir / f"{stem}.pdf"
        await save_upload(request, pdf)

        async with parse_lock:
            await run_in_threadpool(run_parser, pdf)
            folder = unique_folder(stem)
            shutil.move(work_dir / stem, folder)

        logger.info("Saved %s", folder / "article.md")

        return {"folder": folder.name}

    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
