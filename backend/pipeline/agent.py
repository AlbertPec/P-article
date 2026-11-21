"""Runs one pipeline task in a fresh, isolated Claude Code agent."""

import json
import os
import shutil
import subprocess
import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent.parent / "article-skills"
PLUGIN_NAME = "article"


class AgentError(Exception):
    pass


@dataclass(frozen=True)
class AgentRun:
    result: str
    seconds: float
    cost_usd: float
    turns: int


def claude_bin() -> str:
    name = os.environ.get("CLAUDE_BIN") or "claude"
    path = shutil.which(name)

    if not path:
        raise AgentError(f"the claude CLI was not found at {name!r}. Install Claude Code or set CLAUDE_BIN")

    return path


def as_text(output: str | bytes | None) -> str:
    # TimeoutExpired carries bytes even when the process ran in text mode.
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")

    return output or ""


def run_agent(
    skill: str,
    args: str,
    cwd: Path,
    *,
    model: str,
    tools: Sequence[str],
    timeout: int,
    log_path: Path,
) -> AgentRun:
    """Runs /article:<skill> <args> in a new agent whose working folder is cwd."""

    prompt = f"/{PLUGIN_NAME}:{skill} {args}".strip()

    command = [
        claude_bin(),
        "--print",
        "--plugin-dir", str(PLUGIN_DIR),
        # No Bash or WebFetch, no settings files, and the file tools only reach cwd.
        "--restricted",
        # No MCP servers, so the connectors on your account stay out of the agent's context.
        "--strict-mcp-config",
        "--tools", ",".join(tools),
        # Writes are allowed. Anything that would ask for permission is denied instead of waiting.
        "--permission-mode", "acceptEdits",
        "--permission-prompts", "none",
        "--no-session-persistence",
        "--model", model,
        "--output-format", "json",
    ]

    log_path.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()

    try:
        # The prompt goes on stdin: as an argument, the variadic --tools flag could swallow it.
        process = subprocess.run(
            command,
            input=prompt,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        write_log(log_path, prompt, command, None, as_text(exc.stdout), as_text(exc.stderr))
        raise AgentError(f"timed out after {timeout} s (log: {log_path})") from None

    seconds = time.monotonic() - started
    response = write_log(log_path, prompt, command, process.returncode, process.stdout, process.stderr)

    if not isinstance(response, dict):
        detail = process.stderr.strip() or process.stdout.strip() or "no output"
        raise AgentError(f"claude exited with code {process.returncode}: {detail[:300]} (log: {log_path})")

    if process.returncode != 0 or response.get("is_error"):
        detail = str(response.get("result") or response.get("subtype") or "unknown error")
        raise AgentError(f"the agent failed: {detail[:300]} (log: {log_path})")

    return AgentRun(
        result=str(response.get("result", "")),
        seconds=seconds,
        cost_usd=float(response.get("total_cost_usd") or 0),
        turns=int(response.get("num_turns") or 0),
    )


def write_log(
    log_path: Path,
    prompt: str,
    command: list[str],
    returncode: int | None,
    stdout: str,
    stderr: str,
) -> object:
    """Saves everything about one agent run and returns its parsed JSON result, if any."""

    try:
        response = json.loads(stdout)
    except json.JSONDecodeError:
        response = None

    log = {
        "prompt": prompt,
        "command": command,
        "returncode": returncode,
        "response": response if response is not None else stdout,
        "stderr": stderr,
    }

    log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")

    return response
