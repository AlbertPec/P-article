"""The admin web app: the page itself and the small JSON API behind it.

It only listens on this computer (see __main__.py), because it can upload files, run the
pipeline and change the config, and it has no authentication.
"""

import json
import socket
import urllib.request
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse

from pipeline.errors import StageError
from pipeline.parse import ParseError, safe_stem
from pipeline.rewrite import CHOICES, DEFAULT_CONFIG, LENGTH_LIMITS, validate_config

from .jobs import BACKEND_DIR, JobQueue

STATIC_DIR = Path(__file__).resolve().parent / "static"
UPLOADS_DIR = BACKEND_DIR / "uploads"
EMULATOR_HOST = "10.0.2.2"
MAX_UPLOAD_BYTES = 200 * 1024 * 1024


def create_admin_app(
    data_dir: Path,
    api_port: int,
    api_host: str = "0.0.0.0",
    config_path: Path = DEFAULT_CONFIG,
    jobs: JobQueue | None = None,
) -> FastAPI:
    app = FastAPI(title="P-article admin", docs_url=None, redoc_url=None, openapi_url=None)
    jobs = jobs or JobQueue(data_dir, UPLOADS_DIR)

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/server")
    def server() -> dict:
        ips = lan_ips() if api_host == "0.0.0.0" else [api_host]

        return {
            "port": api_port,
            "lan_ips": ips,
            "urls": [f"http://{ip}:{api_port}" for ip in ips],
            "emulator_url": f"http://{EMULATOR_HOST}:{api_port}",
            "reachable": is_reachable("127.0.0.1" if api_host == "0.0.0.0" else api_host, api_port),
        }

    @app.get("/api/config")
    def get_config() -> dict:
        return {
            "path": str(config_path),
            "text": config_path.read_text(encoding="utf-8"),
            "choices": CHOICES,
            "length_limits": LENGTH_LIMITS,
        }

    @app.put("/api/config")
    async def put_config(request: Request) -> dict:
        text = (await request.body()).decode("utf-8", errors="replace")

        try:
            config = json.loads(text)
        except json.JSONDecodeError as exc:
            raise HTTPException(400, f"Not valid JSON: {exc}") from None

        try:
            validate_config(config)
        except StageError as exc:
            raise HTTPException(400, str(exc)) from None

        saved = json.dumps(config, indent=2, ensure_ascii=False) + "\n"
        config_path.write_text(saved, encoding="utf-8")

        return {"text": saved}

    @app.get("/api/jobs")
    def list_jobs() -> list[dict]:
        return jobs.list()

    @app.post("/api/jobs")
    async def add_job(request: Request, name: str) -> dict:
        try:
            stem = safe_stem(name)
        except ParseError as exc:
            raise HTTPException(400, str(exc)) from None

        content = await request.body()

        if not content:
            raise HTTPException(400, "The file is empty")

        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(413, "The file is larger than 200 MB")

        if not content.startswith(b"%PDF"):
            raise HTTPException(400, f"{name} is not a PDF file")

        return jobs.add(f"{stem}.pdf", content).to_dict()

    return app


def lan_ips() -> list[str]:
    """Returns the IPv4 address this computer uses on the local network, or nothing when offline."""

    ips: list[str] = []

    # Connecting a UDP socket sends nothing; it only makes the OS pick the outgoing interface.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("10.255.255.255", 1))
            ips.append(sock.getsockname()[0])
    except OSError:
        pass

    # Not socket.getaddrinfo(socket.gethostname()): on macOS it can block for seconds and then fail.

    return [ip for ip in dict.fromkeys(ips) if not ip.startswith("127.") and ip != "0.0.0.0"]


def is_reachable(host: str, port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://{host}:{port}/articles", timeout=1) as response:
            return response.status == 200
    except OSError:
        return False
