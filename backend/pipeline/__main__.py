"""Runs the article pipeline from the command line. From backend/:

    .venv/bin/python -m pipeline path/to/article.pdf
    .venv/bin/python -m pipeline --folder output/test-article
    .venv/bin/python -m pipeline --folder output/test-article --from headlines
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

from .agent import AgentError, AgentRun, run_agent, skill_prompt
from .parse import ParseError, parse_pdf
from .stages import STAGES, Stage, StageError, numbered_parts, stage_model


def clear_outputs(stage: Stage, article: Path) -> None:
    logs = article / "logs"

    paths = [article / output for output in stage.outputs]
    paths.append(logs / f"{stage.name}.json")
    paths += logs.glob(f"{stage.name}-*.json")

    for path in paths:
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()


def run_stage(stage: Stage, article: Path) -> tuple[int, float, float]:
    """Runs a stage's agent and checks its output.

    Returns how many calls it took, their total time and their total cost.
    """

    clear_outputs(stage, article)

    if stage.prepare:
        stage.prepare(article)

    runs: list[AgentRun] = []
    model = stage_model(stage, article)

    def send(label: str, prompt: str) -> None:
        run = run_agent(
            prompt,
            article,
            model=model,
            tools=stage.tools,
            timeout=stage.timeout,
            log_path=article / "logs" / f"{label}.json",
        )
        runs.append(run)
        print(f"    {run.seconds:.0f} s, {run.turns} turns: {run.result.strip()[:120]}", flush=True)

    if stage.per_part:
        parts = numbered_parts(article / "parts")

        for number, part in enumerate(parts, 1):
            prompt = skill_prompt(stage.skill, stage.args.format(part=part.name, article_id=article.name))
            print(f"[{stage.name} {number}/{len(parts)}] {prompt}", flush=True)
            send(f"{stage.name}-{part.stem}", prompt)

            if stage.check_part:
                try:
                    stage.check_part(article, part.name)
                except StageError as exc:
                    print(f"    check failed: {exc}. Trying once more.", flush=True)
                    send(
                        f"{stage.name}-{part.stem}-retry",
                        f"{prompt}\n\nA previous attempt at this part failed its check: {exc}. "
                        "Fix this and write the part again.",
                    )
                    stage.check_part(article, part.name)
    else:
        prompt = skill_prompt(stage.skill, stage.args.format(article_id=article.name))
        print(f"[{stage.name}] {prompt}", flush=True)
        send(stage.name, prompt)

    if stage.finish:
        for line in stage.finish(article):
            print(f"    {line}", flush=True)

    stage.check(article)

    return len(runs), sum(run.seconds for run in runs), sum(run.cost_usd for run in runs)


def main() -> int:
    stage_names = [stage.name for stage in STAGES]

    parser = argparse.ArgumentParser(
        prog="python -m pipeline",
        description="Parses a PDF, then runs each LLM stage in its own Claude Code agent.",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("pdf", nargs="?", type=Path, help="the PDF to parse and process")
    source.add_argument("--folder", type=Path, help="an article folder in output/ that was already parsed")
    parser.add_argument("--from", dest="start", choices=stage_names, help="the first stage to run (needs --folder)")
    args = parser.parse_args()

    if args.start and not args.folder:
        parser.error("--from needs --folder")

    if args.folder:
        article = args.folder.resolve()

        if not (article / "article.md").is_file():
            parser.error(f"{args.folder} has no article.md")
    else:
        print(f"[parse] {args.pdf}", flush=True)

        try:
            article = parse_pdf(args.pdf.resolve())
        except ParseError as exc:
            print(f"\n[parse] failed: {exc}", file=sys.stderr)
            return 1

        print(f"[parse] saved {article}", flush=True)

    stages = STAGES[stage_names.index(args.start):] if args.start else STAGES
    summary = []

    for stage in stages:
        try:
            calls, seconds, cost = run_stage(stage, article)
        except (AgentError, StageError) as exc:
            print(f"\n[{stage.name}] failed: {exc}", file=sys.stderr)
            print(
                f"Rerun from this stage with: python -m pipeline --folder {os.path.relpath(article)} --from {stage.name}",
                file=sys.stderr,
            )
            return 1

        summary.append((stage.name, calls, seconds, cost))
        print(f"[{stage.name}] done", flush=True)

    print(f"\nDone: {article}")

    for name, calls, seconds, cost in summary:
        print(f"  {name:<10} {calls:>3} call(s)  {seconds:>6.0f} s  ${cost:.4f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
