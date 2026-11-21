import base64
import logging
from http import HTTPStatus
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .dtos import (
    ArticleSummaryDto,
    MetadataDto,
    PanelDto,
    ParticleDto,
    RecommendationsRequest,
    RecommendationsResponse,
)
from .service import NotFound, Service
from .storage import Storage

logger = logging.getLogger(__name__)


def create_app(data_dir: Path) -> FastAPI:
    service = Service(Storage(data_dir))
    app = FastAPI(title="P-article")

    @app.get("/articles")
    def list_articles() -> list[ArticleSummaryDto]:
        return [
            ArticleSummaryDto(id=article.id, particle_count=article.particle_count)
            for article in service.list_articles()
        ]

    @app.get("/articles/{article_id}")
    def get_metadata(article_id: str) -> MetadataDto:
        metadata = service.get_metadata(article_id)

        return MetadataDto(
            id=metadata.id,
            title=metadata.title,
            authors=metadata.authors,
            affiliations=metadata.affiliations,
            topic=metadata.topic,
            particle_count=metadata.particle_count,
        )

    @app.get("/articles/{article_id}/particles/{part_no}/panels")
    def get_panels(article_id: str, part_no: int) -> list[PanelDto]:
        return [
            PanelDto(header=panel.header, image=encode(panel.image))
            for panel in service.get_panels(article_id, part_no)
        ]

    @app.get("/articles/{article_id}/particles/{part_no}")
    def get_particle(article_id: str, part_no: int) -> ParticleDto:
        particle = service.get_particle(article_id, part_no)

        return ParticleDto(
            content=particle.content,
            images={name: encode(image) for name, image in particle.images.items()},
        )

    @app.post("/recommendations")
    def recommend(body: RecommendationsRequest) -> RecommendationsResponse:
        return RecommendationsResponse(article_ids=service.recommend(body.read_article_ids))

    @app.exception_handler(NotFound)
    def handle_not_found(request: Request, error: NotFound) -> JSONResponse:
        return problem(HTTPStatus.NOT_FOUND, str(error))

    @app.exception_handler(StarletteHTTPException)
    def handle_http_error(request: Request, error: StarletteHTTPException) -> JSONResponse:
        return problem(HTTPStatus(error.status_code), error.detail)

    @app.exception_handler(RequestValidationError)
    def handle_validation_error(request: Request, error: RequestValidationError) -> JSONResponse:
        detail = "; ".join(
            f"{'.'.join(str(part) for part in item['loc'])}: {item['msg']}" for item in error.errors()
        )

        return problem(HTTPStatus.UNPROCESSABLE_CONTENT, detail)

    @app.exception_handler(Exception)
    def handle_unexpected_error(request: Request, error: Exception) -> JSONResponse:
        logger.exception("Request %s %s failed", request.method, request.url.path)

        return problem(HTTPStatus.INTERNAL_SERVER_ERROR, "The server failed to read the data")

    return app


def encode(image: bytes) -> str:
    return base64.b64encode(image).decode("ascii")


def problem(status: HTTPStatus, detail: str) -> JSONResponse:
    """Builds an error response in the RFC 9457 format."""

    return JSONResponse(
        status_code=status,
        content={"status": status.value, "title": status.phrase, "detail": detail},
        media_type="application/problem+json",
    )
