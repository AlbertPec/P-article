# P-article parser server

Receives PDFs from the app, parses them with `pdf_to_md_v2.py`, and saves each result in `output/<article name>/`:

- `article.md`: the parsed article
- `images/`: images and tables extracted from it
- a copy of the original PDF

## Setup

Requires Python 3.13.

```sh
cd backend
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Run

```sh
cd backend
.venv/bin/uvicorn server:app --host 127.0.0.1 --port 8000
```

The server has no authentication, so it only listens on this computer. Keep the `127.0.0.1` host.

## Connect the app

**Emulator:** nothing to set up. The app uses `http://10.0.2.2:8000`, which is how an emulator reaches this computer.

**Phone over USB:** forward the port and build the app with the local address:

```sh
adb reverse tcp:8000 tcp:8000
./gradlew installDebug -PparserServerUrl=http://localhost:8000
```

## Test PDF

To put the sample PDF in the Downloads folder of an emulator or connected phone:

```sh
adb push backend/samples/test-article.pdf /sdcard/Download/
```

If it doesn't appear in the file picker, restart the device or open its Files app.

## Pipeline

The pipeline parses a PDF the same way the server does, then runs a series of LLM stages on it. Each stage runs in a fresh local Claude Code agent that only has its own skill and the article folder. For now it runs from the command line only; the server doesn't use it yet.

It needs the `claude` CLI installed and logged in. If `claude` isn't on your `PATH`, set `CLAUDE_BIN` to its location.

```sh
cd backend
.venv/bin/python -m pipeline samples/test-article.pdf                       # parse, then every stage
.venv/bin/python -m pipeline --folder output/test-article                   # rerun every stage, without parsing
.venv/bin/python -m pipeline --folder output/test-article --from headlines  # rerun from one stage onwards
```

Agents use Haiku by default. To use another model for every stage, set `PIPELINE_MODEL`, for example `PIPELINE_MODEL=sonnet`. To change one stage only, set `model=` on that stage.

### What it writes

Everything goes in the article folder `output/<name>/`:

| Path | Written by |
|------|------------|
| `article.md`, `images/` | parse (`pdf_to_md_v2.py`) |
| `parts/part_1.md` … | split: one agent |
| `rewritten/part_1.md` … | rewrite: one agent per part |
| `headers.json` | headlines: one agent, same format as `test_data/test_article/headers.json` |
| `logs/<stage>.json` | every agent run: the prompt, the command and Claude's JSON result |

Paths inside the Markdown files, including image links, are relative to the article folder. So `images/x.png` in `parts/part_3.md` means `output/<name>/images/x.png`.

After each stage, the pipeline checks its output: numbering, empty files, broken image links and the shape of `headers.json`. If a stage fails, the pipeline stops and prints the command that reruns it.

### Skills

The skills live in `article-skills/`, a Claude Code plugin named `article`, and the stage list is in `pipeline/stages.py`. The current skills are mocks:

- **split-article** cuts at numbered sections.
- **rewrite-part** copies the part unchanged.
- **write-headlines** writes placeholder titles.

To replace a mock, edit its `article-skills/skills/<name>/SKILL.md`. To add a stage, add a skill folder there and a `Stage(...)` to `STAGES`.

Each agent runs with:

- **Its working folder:** the article folder, and its file tools can't reach anything outside it.
- **Tools:** Read, Write, Glob, Grep and Skill. There's no Bash, web access or MCP servers.
- **Permissions:** writes are allowed; anything else that would ask for permission is denied.

Agents still see the names and one-line descriptions of your personal skills in `~/.claude/skills` and of Claude Code's built-in skills, but not their full contents.
