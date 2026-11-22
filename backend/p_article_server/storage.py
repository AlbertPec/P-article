"""Reads articles and panel images from the data directory.

Layout:
    <data_dir>/panel_images/<name>.png
    <data_dir>/articles/<article_id>/
        images/<name>.png
        parts/part_<part_no>.md
        particles/part_<part_no>.md
        metadata.json
        panels.json
        original_article.pdf
"""

import json
import re
import uuid
from pathlib import Path

from .models import ArticleSummary, Metadata, Panel, Particle

IMAGE_LINK = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")


class StorageError(Exception):
    """The data on disk doesn't match the expected layout."""


class Storage:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir.resolve()
        self.articles_dir = self.data_dir / "articles"
        self.panel_images_dir = self.data_dir / "panel_images"

    def article_ids(self) -> list[str]:
        """Returns ids of all articles, sorted. Folders that aren't named with a UUID are skipped."""

        if not self.articles_dir.is_dir():
            return []

        return sorted(
            path.name
            for path in self.articles_dir.iterdir()
            if path.is_dir() and is_uuid(path.name) and (path / "metadata.json").is_file()
        )

    def has_article(self, article_id: str) -> bool:
        return is_uuid(article_id) and (self.articles_dir / article_id / "metadata.json").is_file()

    def read_summary(self, article_id: str) -> ArticleSummary:
        metadata = self.read_metadata(article_id)

        return ArticleSummary(id=metadata.id, particle_count=metadata.particle_count)

    def read_metadata(self, article_id: str) -> Metadata:
        raw = self._read_json(self.articles_dir / article_id / "metadata.json")

        try:
            return Metadata(
                id=article_id,
                title=raw["title"],
                authors=raw["authors"],
                affiliations=raw["affiliations"],
                topic=raw["topic"],
                particle_count=raw["particle_count"],
            )
        except (KeyError, TypeError) as error:
            raise StorageError(f"Invalid metadata.json of article {article_id}") from error

    def has_particle(self, article_id: str, part_no: int) -> bool:
        return self._particle_path(article_id, part_no).is_file()

    def read_panels(self, article_id: str, part_no: int) -> list[Panel]:
        raw = self._read_json(self.articles_dir / article_id / "panels.json")

        try:
            entries = raw.get(str(part_no), [])

            return [
                Panel(header=entry["header"], image=self._read_panel_image(entry["image"]))
                for entry in entries
            ]
        except (KeyError, TypeError, AttributeError) as error:
            raise StorageError(f"Invalid panels.json of article {article_id}") from error

    def read_particle(self, article_id: str, part_no: int) -> Particle:
        """Returns the particle text with the images it links to, keyed by file name."""

        content = self._particle_path(article_id, part_no).read_text(encoding="utf-8")
        images_dir = self.articles_dir / article_id / "images"
        images = {}

        for name in IMAGE_LINK.findall(content):
            if name in images:
                continue

            images[name] = self._read_file(images_dir, name)

        return Particle(content=content, images=images)

    def _particle_path(self, article_id: str, part_no: int) -> Path:
        return self.articles_dir / article_id / "particles" / f"part_{part_no}.md"

    def _read_panel_image(self, path: str) -> bytes:
        """Reads an image referenced in panels.json, which must point into panel_images/."""

        prefix = "panel_images/"

        if not path.startswith(prefix):
            raise StorageError(f"Panel image {path} is not in panel_images/")

        return self._read_file(self.panel_images_dir, path.removeprefix(prefix))

    def _read_file(self, directory: Path, name: str) -> bytes:
        """Reads a file by bare name, refusing names that would leave the directory."""

        if Path(name).name != name or name in {".", ".."}:
            raise StorageError(f"Invalid file name {name} in {directory}")

        path = directory / name

        if not path.is_file():
            raise StorageError(f"Missing file {path}")

        return path.read_bytes()

    def _read_json(self, path: Path):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise StorageError(f"Cannot read {path}") from error


def is_uuid(value: str) -> bool:
    try:
        return str(uuid.UUID(value)) == value
    except ValueError:
        return False
