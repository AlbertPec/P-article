import json
import sys
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from admin.app import create_admin_app
from admin.jobs import JobQueue

CONFIG = {
    "model": "sonnet",
    "audience": "curious adults",
    "language": "same as the original",
    "style": "friendly",
    "explanation": "moderate",
    "metaphors": "occasional",
    "sentences": "shorter",
    "length": {"min_ratio": 0.85, "max_ratio": 1.3},
    "extra_instructions": "",
}
PDF = b"%PDF-1.4 test"


def fake_command(exit_code: int):
    def command(pdf: Path, data_dir: Path) -> list[str]:
        return [sys.executable, "-c", f"print('parsing', {str(pdf)!r}); raise SystemExit({exit_code})"]

    return command


def wait_for(jobs: JobQueue, status: str) -> dict:
    for _ in range(100):
        job = jobs.list()[0]
        if job["status"] == status:
            return job
        time.sleep(0.05)
    raise AssertionError(f"job is {job['status']}, expected {status}")


@pytest.fixture
def config_path(tmp_path: Path) -> Path:
    path = tmp_path / "rewrite-config.json"
    path.write_text(json.dumps(CONFIG))
    return path


def make_client(tmp_path: Path, config_path: Path, exit_code: int = 0) -> tuple[TestClient, JobQueue]:
    jobs = JobQueue(tmp_path / "data", tmp_path / "uploads", command=fake_command(exit_code))
    app = create_admin_app(tmp_path / "data", api_port=59999, config_path=config_path, jobs=jobs)
    return TestClient(app), jobs


def test_page_is_served(tmp_path, config_path):
    client, _ = make_client(tmp_path, config_path)

    response = client.get("/")

    assert response.status_code == 200
    assert "<title>P-article Admin</title>" in response.text


def test_server_info(tmp_path, config_path):
    client, _ = make_client(tmp_path, config_path)

    info = client.get("/api/server").json()

    assert info["port"] == 59999
    assert info["emulator_url"] == "http://10.0.2.2:59999"
    assert info["reachable"] is False
    assert all(not ip.startswith("127.") for ip in info["lan_ips"])
    assert info["urls"] == [f"http://{ip}:59999" for ip in info["lan_ips"]]


def test_get_config(tmp_path, config_path):
    client, _ = make_client(tmp_path, config_path)

    config = client.get("/api/config").json()

    assert json.loads(config["text"]) == CONFIG
    assert "friendly" in config["choices"]["style"]


def test_save_valid_config(tmp_path, config_path):
    client, _ = make_client(tmp_path, config_path)
    changed = CONFIG | {"style": "formal"}

    response = client.put("/api/config", content=json.dumps(changed))

    assert response.status_code == 200
    assert json.loads(config_path.read_text()) == changed
    assert config_path.read_text().endswith("}\n")


@pytest.mark.parametrize(
    "body, message",
    [
        ("{not json", "Not valid JSON"),
        (json.dumps(CONFIG | {"style": "weird"}), 'rewrite setting "style"'),
        (json.dumps(CONFIG | {"colour": "red"}), "unknown rewrite settings"),
    ],
)
def test_invalid_config_is_not_saved(tmp_path, config_path, body, message):
    client, _ = make_client(tmp_path, config_path)
    before = config_path.read_text()

    response = client.put("/api/config", content=body)

    assert response.status_code == 400
    assert message in response.json()["detail"]
    assert config_path.read_text() == before


@pytest.mark.parametrize(
    "name, content",
    [("notes.txt", PDF), ("paper.pdf", b"hello"), ("paper.pdf", b"")],
)
def test_bad_upload_is_rejected(tmp_path, config_path, name, content):
    client, jobs = make_client(tmp_path, config_path)

    response = client.post("/api/jobs", params={"name": name}, content=content)

    assert response.status_code == 400
    assert jobs.list() == []


def test_upload_runs_pipeline(tmp_path, config_path):
    client, jobs = make_client(tmp_path, config_path)

    response = client.post("/api/jobs", params={"name": "My Paper.pdf"}, content=PDF)

    assert response.status_code == 200
    assert response.json()["name"] == "My_Paper.pdf"
    job = wait_for(jobs, "done")
    assert job["exit_code"] == 0
    assert "parsing" in job["log"][0]
    # The upload is removed once the pipeline has copied it into output/.
    assert not any((tmp_path / "uploads").iterdir())


def test_failed_pipeline_marks_job_failed(tmp_path, config_path):
    client, jobs = make_client(tmp_path, config_path, exit_code=1)

    client.post("/api/jobs", params={"name": "paper.pdf"}, content=PDF)

    assert wait_for(jobs, "failed")["exit_code"] == 1
