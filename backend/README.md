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

Every stage runs on Sonnet. Rewrite's model is the `model` setting in `rewrite-config.json` (see "How rewrite runs"). To change another stage, set `model=` on its `Stage` in `pipeline/stages.py`. To use one model for every stage, for example while testing, set `PIPELINE_MODEL`, such as `PIPELINE_MODEL=haiku`.

### What it writes

Everything goes in the article folder `output/<name>/`:

| Path | Written by |
|------|------------|
| `article.md`, `images/` | parse (`pdf_to_md_v2.py`) |
| `split-outline.md` | split: the article's numbered blocks with their reading times, for the agent |
| `split-plan.json` | split: the agent's plan, saying which blocks go into each part and which are deleted |
| `parts/part_1.md` … | split: the article cut along the plan, see "How split runs" below |
| `dropped.md` | split: the deleted blocks (journal headers, logos, running headers, boilerplate, authors), each with the reason, for review |
| `back-matter.md` | split: CRediT, declarations, acknowledgements and references, kept out of the parts |
| `metadata.json` | split: `{"authors": [...], "affiliations": [...], "topic": "..."}` |
| `abstract.md` | split: the abstract and keywords, kept out of the parts and given to later stages as context |
| `rewrite-settings.json` | rewrite: the style settings the agents follow, with each part's word budget |
| `rewritten/part_1.md` … | rewrite: a fresh agent per part, see "How rewrite runs" below. `parts/` is never changed. |
| `rewrite-notes.md` | rewrite: the short memory passed from part to part |
| `headers.json` | headlines: 3 short, catchy headlines per part, from one agent, in the same format as `test_data/test_article/headers.json` |
| `logs/<stage>.json` | every call: the prompt, the command and Claude's JSON result. Rewrite also writes `rewrite-part_<n>.json` for each part. |

Paths inside the Markdown files, including image links, are relative to the article folder. So `images/x.png` in `parts/part_3.md` means `output/<name>/images/x.png`.

After each stage, the pipeline checks its output: numbering, empty files, broken image links and the shape of `headers.json`. If a stage fails, the pipeline stops and prints the command that reruns it.

### How split runs

Split cuts the article into parts that each take 4-5 minutes to read and end on a finished thought. The work is shared between Python and the agent, so the agent only does what needs judgement.

1. **Python numbers the blocks.** `pipeline/split.py` breaks `article.md` into blocks (paragraphs, headings, graphics and the parser's text versions of equations) and writes `split-outline.md`. For each block it lists the lines, words, graphics and reading time. Reading time is 230 words per minute plus 10 seconds per graphic; both numbers are set at the top of `split.py`.
2. **The agent plans the parts.** It reads the outline and the article, then writes two files:
   - `split-plan.json`, saying which blocks go into each part, which blocks to delete and where the back matter starts
   - `metadata.json`, with the authors, affiliations and topic
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

### Skills

The skills live in `article-skills/`, a Claude Code plugin named `article`, and the stage list is in `pipeline/stages.py`.

- **split-article:** the real skill, described above.
- **rewrite-part:** the real skill, described above.
- **write-headlines:** one agent reads every rewritten part and writes 3 short, catchy, slightly clickbaity headlines for each, with different angles and no repeated patterns across the article. It's based on `test_data/initial_headers_prompt.txt`. The check rejects a headline over 70 characters (the skill aims for 60), a repeated headline, and any number that isn't in that part or the abstract.

To change a skill, edit its `article-skills/skills/<name>/SKILL.md`. To add a stage, add a skill folder there and a `Stage(...)` to `STAGES`. A stage can also run Python before and after its agent, with `prepare` and `finish`, as split and rewrite do.

Each agent runs with:

- **Its working folder:** the article folder, and its file tools can't reach anything outside it.
- **Tools:** Read, Write, Glob, Grep and Skill, plus Edit for rewrite. There's no Bash, web access or MCP servers.
- **Permissions:** writes are allowed; anything else that would ask for permission is denied.

Agents still see the names and one-line descriptions of your personal skills in `~/.claude/skills` and of Claude Code's built-in skills, but not their full contents.
