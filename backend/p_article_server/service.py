from .models import ArticleSummary, Metadata, Panel, Particle
from .storage import Storage


class NotFound(Exception):
    """The requested article or particle doesn't exist."""


class Service:
    def __init__(self, storage: Storage):
        self.storage = storage

    def list_articles(self) -> list[ArticleSummary]:
        return [self.storage.read_summary(article_id) for article_id in self.storage.article_ids()]

    def get_metadata(self, article_id: str) -> Metadata:
        self._require_article(article_id)

        return self.storage.read_metadata(article_id)

    def get_panels(self, article_id: str, part_no: int) -> list[Panel]:
        self._require_particle(article_id, part_no)

        return self.storage.read_panels(article_id, part_no)

    def get_particle(self, article_id: str, part_no: int) -> Particle:
        self._require_particle(article_id, part_no)

        return self.storage.read_particle(article_id, part_no)

    def recommend(self, read_article_ids: list[str]) -> list[str]:
        """Recommends every article that hasn't been read yet. Unknown ids are ignored."""

        read = set(read_article_ids)

        return [article_id for article_id in self.storage.article_ids() if article_id not in read]

    def _require_article(self, article_id: str) -> None:
        if not self.storage.has_article(article_id):
            raise NotFound(f"Article {article_id} does not exist")

    def _require_particle(self, article_id: str, part_no: int) -> None:
        self._require_article(article_id)

        if not self.storage.has_particle(article_id, part_no):
            raise NotFound(f"Particle {part_no} of article {article_id} does not exist")
