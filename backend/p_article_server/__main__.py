import argparse
from pathlib import Path

import uvicorn

from .api import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description="Serves processed articles to the P-article app.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="directory with articles/ and panel_images/ (default: data)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="address to listen on; use 0.0.0.0 to reach the server from the local network (default: 127.0.0.1)",
    )
    parser.add_argument("--port", type=int, default=8000, help="port to listen on (default: 8000)")
    args = parser.parse_args()

    if not (args.data_dir / "articles").is_dir():
        parser.error(f"{args.data_dir} has no articles/ directory")

    uvicorn.run(create_app(args.data_dir), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
