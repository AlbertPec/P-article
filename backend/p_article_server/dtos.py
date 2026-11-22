from pydantic import BaseModel


class ArticleSummaryDto(BaseModel):
    id: str
    particle_count: int


class MetadataDto(BaseModel):
    id: str
    title: str
    authors: list[str]
    affiliations: list[str]
    topic: str
    particle_count: int


class PanelDto(BaseModel):
    header: str
    image: str


class ParticleDto(BaseModel):
    content: str
    images: dict[str, str]


class RecommendationsRequest(BaseModel):
    read_article_ids: list[str]


class RecommendationsResponse(BaseModel):
    article_ids: list[str]
