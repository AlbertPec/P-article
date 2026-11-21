"""Starts the admin page and the article API server together. From backend/:

    .venv/bin/python -m admin

The admin page listens only on this computer (127.0.0.1:8001). The API server, which the
phone app reads from, listens on the local network (0.0.0.0:8005).
"""

import argparse
import threading
import time
from pathlib import Path

import uvicorn

from p_article_server.api import create_app

from .app import create_admin_app, lan_ips


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m admin",
        description="Serves the admin page and the article API for the P-article app.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="the server's data folder, which the pipeline exports to (default: data)",
    )
    parser.add_argument("--port", type=int, default=8001, help="port of the admin page (default: 8001)")
    parser.add_argument(
        "--api-host",
        default="0.0.0.0",
        help="address the API server listens on (default: 0.0.0.0, the local network)",
    )
    parser.add_argument("--api-port", type=int, default=8005, help="port of the API server (default: 8005)")
    args = parser.parse_args()

    data_dir = args.data_dir.resolve()
    (data_dir / "articles").mkdir(parents=True, exist_ok=True)
    (data_dir / "panel_images").mkdir(exist_ok=True)

    api_server = uvicorn.Server(uvicorn.Config(create_app(data_dir), host=args.api_host, port=args.api_port))
    api_thread = threading.Thread(target=api_server.run, name="api-server", daemon=True)
    api_thread.start()

    # Wait until the API server listens, so a port that's already taken stops everything here.
    while not api_server.started:
        if not api_thread.is_alive():
            raise SystemExit(f"The API server could not start on {args.api_host}:{args.api_port} (see the error above)")
        time.sleep(0.05)

    print(f"Admin page:  http://127.0.0.1:{args.port}", flush=True)
    for ip in lan_ips() if args.api_host == "0.0.0.0" else [args.api_host]:
        print(f"App server:  http://{ip}:{args.api_port}", flush=True)

    try:
        uvicorn.run(create_admin_app(data_dir, args.api_port, args.api_host), host="127.0.0.1", port=args.port)
    finally:
        api_server.should_exit = True
        api_thread.join(timeout=5)


if __name__ == "__main__":
    main()
