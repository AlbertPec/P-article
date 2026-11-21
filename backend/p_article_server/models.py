from dataclasses import dataclass


@dataclass(frozen=True)
class ArticleSummary:
    id: str
    particle_count: int


@dataclass(frozen=True)
class Metadata:
    id: str
    title: str
    authors: list[str]
    affiliations: list[str]
    topic: str
    particle_count: int


@dataclass(frozen=True)
class Panel:
    header: str
    image: bytes


@dataclass(frozen=True)
class Particle:
    content: str
    images: dict[str, bytes]
