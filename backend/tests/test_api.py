import base64
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from p_article_server.api import create_app

ARTICLE_ID = "3f2b8c1e-7d4a-4e6b-9a1f-2c5d8e0b4a71"
OTHER_ID = "9c7e1a2d-5b3f-4c8e-a6d0-1f4b7e9c2a35"
METADATA = {
    "title": "Title",
    "authors": ["Author"],
    "affiliations": ["University"],
    "topic": "Topic",
    "particle_count": 2,
}


def write_article(data_dir: Path, article_id: str, particles: dict[int, str], panels: dict) -> Path:
    article = data_dir / "articles" / article_id
    (article / "particles").mkdir(parents=True)
    (article / "images").mkdir()
    (article / "metadata.json").write_text(json.dumps(METADATA | {"particle_count": len(particles)}))
    (article / "panels.json").write_text(json.dumps(panels))

    for part_no, content in particles.items():
        (article / "particles" / f"part_{part_no}.md").write_text(content)

    return article


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    (tmp_path / "panel_images").mkdir()
    (tmp_path / "panel_images" / "sea.png").write_bytes(b"sea")

    article = write_article(
        tmp_path,
        ARTICLE_ID,
        particles={1: "Text ![Fig](fig1.png) and ![](fig1.png)", 2: "No images"},
        panels={"1": [{"header": "Header A", "image": "panel_images/sea.png"}]},
    )
    (article / "images" / "fig1.png").write_bytes(b"fig1")
    (article / "images" / "unused.png").write_bytes(b"unused")

    write_article(tmp_path, OTHER_ID, particles={1: "Other"}, panels={})
    (tmp_path / "articles" / "not-a-uuid").mkdir()

    return tmp_path


@pytest.fixture
def client(data_dir: Path) -> TestClient:
    return TestClient(create_app(data_dir), raise_server_exceptions=False)


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def assert_problem(response, status: int) -> None:
    assert response.status_code == status
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["status"] == status


def test_list_articles(client):
    response = client.get("/articles")

    assert response.status_code == 200
    assert response.json() == [
        {"id": ARTICLE_ID, "particle_count": 2},
        {"id": OTHER_ID, "particle_count": 1},
    ]


def test_get_metadata(client):
    response = client.get(f"/articles/{ARTICLE_ID}")

    assert response.status_code == 200
    assert response.json() == {"id": ARTICLE_ID} | METADATA


def test_get_panels(client):
    response = client.get(f"/articles/{ARTICLE_ID}/particles/1/panels")

    assert response.status_code == 200
    assert response.json() == [{"header": "Header A", "image": b64(b"sea")}]


def test_get_panels_of_particle_without_panels(client):
    response = client.get(f"/articles/{ARTICLE_ID}/particles/2/panels")

    assert response.status_code == 200
    assert response.json() == []


def test_get_particle_sends_only_linked_images(client):
    response = client.get(f"/articles/{ARTICLE_ID}/particles/1")

    assert response.status_code == 200
    assert response.json() == {
        "content": "Text ![Fig](fig1.png) and ![](fig1.png)",
        "images": {"fig1.png": b64(b"fig1")},
    }


@pytest.mark.parametrize(
    "path",
    [
        f"/articles/{OTHER_ID.replace('9', '8')}",
        "/articles/not-a-uuid",
        "/articles/..",
        f"/articles/{ARTICLE_ID}/particles/3",
        f"/articles/{ARTICLE_ID}/particles/0",
        f"/articles/{ARTICLE_ID}/particles/3/panels",
        "/unknown",
    ],
)
def test_not_found(client, path):
    assert_problem(client.get(path), 404)


def test_invalid_part_no(client):
    assert_problem(client.get(f"/articles/{ARTICLE_ID}/particles/abc"), 422)


def test_recommendations_skip_read_and_ignore_unknown(client):
    response = client.post("/recommendations", json={"read_article_ids": [ARTICLE_ID, "unknown"]})

    assert response.status_code == 200
    assert response.json() == {"article_ids": [OTHER_ID]}


def test_recommendations_invalid_body(client):
    assert_problem(client.post("/recommendations", json={"ids": []}), 422)


def test_missing_image_is_server_error(client, data_dir):
    (data_dir / "articles" / ARTICLE_ID / "images" / "fig1.png").unlink()

    assert_problem(client.get(f"/articles/{ARTICLE_ID}/particles/1"), 500)


def test_image_link_outside_images_dir_is_server_error(client, data_dir):
    (data_dir / "articles" / ARTICLE_ID / "particles" / "part_2.md").write_text("![](../metadata.json)")

    assert_problem(client.get(f"/articles/{ARTICLE_ID}/particles/2"), 500)
