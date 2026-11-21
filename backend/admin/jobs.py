"""Runs uploaded PDFs through the pipeline, one at a time, in a background thread.

Each job runs the pipeline's own command line (python -m pipeline <pdf>) as a subprocess, so the
pipeline works exactly as it does from a terminal. Jobs are kept in memory only: the results
themselves are in output/ and data/.
"""

import queue
import shutil
import subprocess
import sys
import threading
import time
import uuid
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
LOG_LINES = 200


@dataclass
class Job:
    id: str
    name: str
    pdf: Path
    status: str = "queued"  # queued, running, done or failed
    created: float = field(default_factory=time.time)
    started: float | None = None
    finished: float | None = None
    exit_code: int | None = None
    log: deque[str] = field(default_factory=lambda: deque(maxlen=LOG_LINES))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "created": self.created,
            "started": self.started,
            "finished": self.finished,
            "exit_code": self.exit_code,
            "log": list(self.log),
        }


def pipeline_command(pdf: Path, data_dir: Path) -> list[str]:
    return [sys.executable, "-u", "-m", "pipeline", str(pdf), "--data-dir", str(data_dir)]


class JobQueue:
    def __init__(
        self,
        data_dir: Path,
        uploads_dir: Path,
        command: Callable[[Path, Path], list[str]] = pipeline_command,
    ):
        self.data_dir = data_dir.resolve()
        self.uploads_dir = uploads_dir
        self.command = command
        self.jobs: list[Job] = []
        self.lock = threading.Lock()
        self.pending: queue.Queue[Job] = queue.Queue()
        self.worker = threading.Thread(target=self._work, name="pipeline-jobs", daemon=True)
        self.worker.start()

    def add(self, name: str, content: bytes) -> Job:
        """Saves the uploaded PDF and queues it."""

        job_id = uuid.uuid4().hex[:12]
        folder = self.uploads_dir / job_id
        folder.mkdir(parents=True)
        pdf = folder / name
        pdf.write_bytes(content)

        job = Job(id=job_id, name=name, pdf=pdf)

        with self.lock:
            self.jobs.append(job)

        self.pending.put(job)

        return job

    def list(self) -> list[dict]:
        with self.lock:
            return [job.to_dict() for job in reversed(self.jobs)]

    def _work(self) -> None:
        while True:
            job = self.pending.get()

            try:
                self._run(job)
            finally:
                shutil.rmtree(job.pdf.parent, ignore_errors=True)
                self.pending.task_done()

    def _run(self, job: Job) -> None:
        job.status = "running"
        job.started = time.time()

        try:
            process = subprocess.Popen(
                self.command(job.pdf, self.data_dir),
                cwd=BACKEND_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                text=True,
                bufsize=1,
            )
        except OSError as exc:
            job.log.append(f"Could not start the pipeline: {exc}")
            job.status = "failed"
            job.finished = time.time()
            return

        assert process.stdout is not None

        for line in process.stdout:
            job.log.append(line.rstrip("\n"))

        job.exit_code = process.wait()
        job.status = "done" if job.exit_code == 0 else "failed"
        job.finished = time.time()
