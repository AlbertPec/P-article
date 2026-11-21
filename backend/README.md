# P-article backend

The backend has two parts:

- **The server** (`p_article_server/`) serves processed articles to the app through a read-only REST API. The API and the data layout are described in `../high-level-architecture-v2.md`.
- **The pipeline** (`pipeline/`) turns a PDF into parts, rewritten parts, headlines and the article's metadata, using the parser `pdf_to_md.py` and local Claude Code agents, then exports the result to the server's `data/`. See "Pipeline" below.

## Setup

Requires Python 3.14.

```sh
cd backend
python3.14 -m venv .venv
.venv/bin/pip install -e ".[pipeline,dev]"
```

`pipeline` installs the parser's dependencies and `dev` the test tools. The server alone needs neither.

## Run the server

```sh
cd backend
.venv/bin/p-article-server --data-dir data
```

`data/` must contain `articles/`, laid out as in `../high-level-architecture-v2.md`. The pipeline's export stage writes it (see "How export runs"). The server has no authentication, so by default it only listens on this computer. Use `--host 0.0.0.0` only on a network you trust, and `--port` to change the port from 8000.

## Tests

```sh
cd backend
.venv/bin/pytest
```

## Connect the app

**Emulator:** nothing to set up. The app uses `http://10.0.2.2:8000`, which is how an emulator reaches this computer.

**Phone over USB:** forward the port and build the app with the local address:

```sh
adb reverse tcp:8000 tcp:8000
./gradlew installDebug -PparserServerUrl=http://localhost:8000
```

## Pipeline

The pipeline parses a PDF with `pdf_to_md.py`, then runs a series of LLM stages on it, and ends with two Python-only stages, `metadata` and `export`. Each LLM stage runs in a fresh local Claude Code agent that only has its own skill and the article folder. It runs from the command line, and works in its own working folders in `output/`. Only the last stage, export, writes to the server's `data/`.

It needs the `claude` CLI installed and logged in. If `claude` isn't on your `PATH`, set `CLAUDE_BIN` to its location.

```sh
cd backend
.venv/bin/python -m pipeline path/to/test-article.pdf                       # parse, then every stage
.venv/bin/python -m pipeline --folder output/test-article                   # rerun every stage, without parsing
.venv/bin/python -m pipeline --folder output/test-article --from headlines  # rerun from one stage onwards
.venv/bin/python -m pipeline --folder output/test-article --from export     # only export again
.venv/bin/python -m pipeline path/to/test-article.pdf --data-dir ../data     # export somewhere other than backend/data
```

Every stage runs on Sonnet. Rewrite's model is the `model` setting in `rewrite-config.json` (see "How rewrite runs"). To change another stage, set `model=` on its `Stage` in `pipeline/stages.py`. To use one model for every stage, for example while testing, set `PIPELINE_MODEL`, such as `PIPELINE_MODEL=haiku`.

### What it writes

Everything except the export goes in the article folder `output/<name>/`:

| Path | Written by |
|------|------------|
| `article.md`, `images/` | parse (`pdf_to_md.py`) |
| `split-outline.md` | split: the article's numbered blocks with their reading times, for the agent |
| `split-plan.json` | split: the agent's plan, saying which blocks go into each part and which are deleted |
| `parts/part_1.md` … | split: the article cut along the plan, see "How split runs" below |
| `dropped.md` | split: the deleted blocks (journal headers, logos, running headers, boilerplate, authors), each with the reason, for review |
| `back-matter.md` | split: CRediT, declarations, acknowledgements and references, kept out of the parts |
| `article-id.txt` | the pipeline, the first time it runs on the folder: the article's UUID, see "How metadata runs" below |
| `metadata.json` | split: `{"title": "...", "authors": [...], "affiliations": [...], "topic": "..."}`. The metadata stage then adds `id` and `particle_count`. |
| `abstract.md` | split: the abstract and keywords, kept out of the parts and given to later stages as context |
| `rewrite-settings.json` | rewrite: the style settings the agents follow, with each part's word budget |
| `rewritten/part_1.md` … | rewrite: a fresh agent per part, see "How rewrite runs" below. `parts/` is never changed. |
| `rewrite-notes.md` | rewrite: the short memory passed from part to part |
| `headers.json` | headlines: 3 short, catchy headlines per part, from one agent, in the same format as `test_data/test_article/headers.json`, with the article's UUID as `article_id` |
| `logs/<stage>.json` | every call: the prompt, the command and Claude's JSON result. Rewrite also writes `rewrite-part_<n>.json` for each part. |

Paths inside the Markdown files, including image links, are relative to the article folder. So `images/x.png` in `parts/part_3.md` means `output/<name>/images/x.png`.

After each stage, the pipeline checks its output: numbering, empty files, broken image links and the shape of `headers.json`. If a stage fails, the pipeline stops and prints the command that reruns it.

### How split runs

Split cuts the article into parts that each take 4-5 minutes to read and end on a finished thought. The work is shared between Python and the agent, so the agent only does what needs judgement.

1. **Python numbers the blocks.** `pipeline/split.py` breaks `article.md` into blocks (paragraphs, headings, graphics and the parser's text versions of equations) and writes `split-outline.md`. For each block it lists the lines, words, graphics and reading time. Reading time is 230 words per minute plus 10 seconds per graphic; both numbers are set at the top of `split.py`.
2. **The agent plans the parts.** It reads the outline and the article, then writes two files:
   - `split-plan.json`, saying which blocks go into each part, which blocks to delete and where the back matter starts
   - `metadata.json`, with the title, authors, affiliations and topic
   - `abstract.md`, the abstract and keywords as plain text, copied word for word, or transcribed when the PDF has the abstract only as an image. The abstract is removed from part 1, and the rewrite and headline agents get this file as context about the whole article.

   The skill in `article-skills/skills/split-article/SKILL.md` sets the priorities:
   1. Delete what isn't the article itself: the journal masthead, logos, badges, running headers and footers, publishing boilerplate and contact details. The authors and affiliations go to the metadata, and the abstract to `abstract.md`.
   2. End each part on a finished thought, at the strongest boundary available: a section heading, then a subsection heading, then a change of topic. Never split a derivation.
   3. Aim for 4-5 minutes, within roughly 3:30 to 6:00 when that's what a clean boundary needs.
   4. Keep each graphic with its text.
   5. Keep the back matter out of the parts.

   The agent opens any graphic it's unsure about before deleting it. In the test article, the first page's "Table 1" image is really the abstract.
3. **Python cuts the article.** It cuts `article.md` along the plan, byte for byte, and moves the deleted blocks to `dropped.md`. Every kept graphic link stays exactly as in the original, in the part where it appears. The check confirms that every block of `article.md` ended up in exactly one place (a part, `dropped.md` or `back-matter.md`), and that `metadata.json` has the right shape.

The pipeline prints each part's reading time. It also warns about a part that is outside 4-5 minutes, or that starts or ends with a graphic. These are warnings, not errors, because a part that ends on a finished thought is worth a slightly uneven length. A heading at the end of a part is always a mistake, so Python moves it to the start of the next part and reports the fix.

### How rewrite runs

Rewrite turns each part into text the app's readers can follow, in the style set in `rewrite-config.json`. It changes how things are said, never the data. The rewrites go to `rewritten/`, and the original parts in `parts/` stay as split cut them.

#### The style settings

`rewrite-config.json`, next to this README, holds the default style:

```json
{
  "model": "sonnet",
  "audience": "curious adults with no background in the field",
  "language": "same as the original",
  "style": "friendly",
  "explanation": "moderate",
  "metaphors": "occasional",
  "sentences": "shorter",
  "length": {"min_ratio": 0.85, "max_ratio": 1.3},
  "extra_instructions": ""
}
```

| Setting | Values |
|---------|--------|
| `model` | the Claude model that rewrites: `sonnet`, `opus` or `haiku` |
| `audience` | free text: who the text is for |
| `language` | `same as the original`, or a language to translate into, such as `Polish` |
| `style` | `formal`, `neutral`, `friendly`, `catchy` |
| `explanation` | how much is added for readers new to the field: `none`, `light`, `moderate`, `thorough` |
| `metaphors` | `none`, `occasional`, `frequent` |
| `sentences` | `as_original`, `shorter`, `short_and_simple` |
| `length` | how long the rewritten text may be, compared with the original: `min_ratio` from 0.5 to 1, `max_ratio` from 1 to 2. With `explanation: thorough`, consider raising `max_ratio`. |
| `extra_instructions` | free text for anything else |

What each value means for the writing is in `article-skills/skills/rewrite-part/SKILL.md`. To add a value, add it there and to `CHOICES` in `pipeline/rewrite.py`.

To give one article its own style, put a `rewrite-config.json` in its folder with only the settings it changes, for example `{"style": "formal", "length": {"max_ratio": 1.5}}`. The pipeline checks the settings before any agent runs and stops on an unknown setting or value.

#### How it runs

Before the agents start, Python merges the settings and writes `rewrite-settings.json`, which adds each part's word budget. Then a fresh agent runs for each part, in order. Each agent reads:

- the settings and the abstract
- the original part
- the previous rewritten part, for continuity
- `rewrite-notes.md`, a short notes file with the voice, the terms, what has already been explained and the metaphors used so far

The agent writes its part, then rewrites the notes for the parts after it. So every part's context stays about the same size however long the article is, and decisions made in part 1 still reach part 6.

#### What the check enforces

After each part, Python compares the rewritten part with the original. It fails the part if:

- any graphic, picture-text block (the parser's text version of an equation or table) or caption isn't copied byte for byte, as its own block, in the original order. A graphic may move to the end of its paragraph, which repairs sentences that the PDF's page breaks cut in half.
- a number from the original text is missing, for example because it was rounded or written in words
- a number appears that isn't in the original part or the abstract
- the text, without graphics, is outside the `length` range. Parts under 60 words aren't checked for length.
- the notes are missing, or longer than 8000 characters
- `parts/` no longer matches what split cut from `article.md`

A part that fails gets one more fresh agent, which is told what failed and fixes it. The pipeline prints each part's word count before and after.

To make another stage work part by part, set `per_part=True` and `check_part` on its `Stage`.

### How metadata runs

Metadata has no agent. `pipeline/metadata.py` completes `metadata.json` with the two fields the server needs to list the article (see `../high-level-architecture-v2.md`):

- `id`: the article_id, a UUIDv4. The pipeline creates it the first time it runs on an article folder and saves it in `article-id.txt`. No stage clears that file, so every rerun keeps the same id, including a rerun of split. Headlines write the same id into `headers.json`.
- `particle_count`: the number of parts in `rewritten/`.

The result has the keys `id`, `title`, `authors`, `affiliations`, `topic` and `particle_count`, in that order. The check confirms those are the only keys, that `id` is a UUIDv4 and that `particle_count` matches `rewritten/`.

### How export runs

Export has no agent either. `pipeline/export.py` copies the finished article into the server's data folder, `backend/data/` by default or the folder given with `--data-dir`:

| In `data/articles/<id>/` | From the article folder |
|------|------|
| `images/` | `images/`, every image the parser extracted |
| `parts/` | `parts/` |
| `particles/` | `rewritten/` |
| `metadata.json` | `metadata.json` |
| `original_article.pdf` | the PDF that parse copied in |

The server finds images by bare file name in `images/`, so links like `images/x.png` become `x.png` in `parts/` and `particles/`. Nothing else in the text changes. An earlier export of the same article is replaced. The check then reads the export back with the server's own code: the article must be listed, its metadata readable, and every particle's images found.

`panels.json` isn't written yet. It pairs each headline with a panel image, and no stage makes panel images yet, so the panels endpoint fails for exported articles.

### Skills

The skills live in `article-skills/`, a Claude Code plugin named `article`, and the stage list is in `pipeline/stages.py`.

- **split-article:** the real skill, described above.
- **rewrite-part:** the real skill, described above.
- **write-headlines:** one agent reads every rewritten part and writes 3 short, catchy, slightly clickbaity headlines for each, with different angles and no repeated patterns across the article. It's based on `test_data/initial_headers_prompt.txt`. The check rejects a headline over 70 characters (the skill aims for 60), a repeated headline, and any number that isn't in that part or the abstract.

To change a skill, edit its `article-skills/skills/<name>/SKILL.md`. To add a stage, add a skill folder there and a `Stage(...)` to `STAGES`. A stage with `skill=None` runs no agent, only its Python, as metadata and export do. A stage can also run Python before and after its agent, with `prepare` and `finish`, as split and rewrite do.

Each agent runs with:

- **Its working folder:** the article folder, and its file tools can't reach anything outside it.
- **Tools:** Read, Write, Glob, Grep and Skill, plus Edit for rewrite. There's no Bash, web access or MCP servers.
- **Permissions:** writes are allowed; anything else that would ask for permission is denied.

Agents still see the names and one-line descriptions of your personal skills in `~/.claude/skills` and of Claude Code's built-in skills, but not their full contents.
