"""Runs the article pipeline from the command line. From backend/:

    .venv/bin/python -m pipeline samples/test-article.pdf
    .venv/bin/python -m pipeline --folder output/test-article
    .venv/bin/python -m pipeline --folder output/test-article --from headlines
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

from .agent import AgentError, run_agent
from .parse import ParseError, parse_pdf
from .stages import DEFAULT_MODEL, STAGES, Stage, StageError, numbered_parts


def clear_outputs(stage: Stage, article: Path) -> None:
    logs = article / "logs"

    paths = [article / output for output in stage.outputs]
    paths += logs.glob(f"{stage.name}.json")
    paths += logs.glob(f"{stage.name}-part_*.json")

    for path in paths:
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()


def run_stage(stage: Stage, article: Path) -> tuple[int, float, float]:
    """Runs a stage's agents one after another, then checks their output.

    Returns how many agents ran, their total time and their total cost.
    """

    clear_outputs(stage, article)

    if stage.parts_from:
        jobs = [(f"{stage.name}-{part.stem}", part.name) for part in numbered_parts(article / stage.parts_from)]
    else:
        jobs = [(stage.name, None)]

    seconds = 0.0
    cost = 0.0

    for number, (label, part) in enumerate(jobs, 1):
        args = stage.args.format(part=part, article_id=article.name)
        progress = f" {number}/{len(jobs)}" if part else ""
        print(f"[{stage.name}{progress}] /article:{stage.skill} {args}", flush=True)

        run = run_agent(
            stage.skill,
            args,
            article,
            model=stage.model or DEFAULT_MODEL,
            tools=stage.tools,
            timeout=stage.timeout,
            log_path=article / "logs" / f"{label}.json",
        )

        seconds += run.seconds
        cost += run.cost_usd
        print(f"    {run.seconds:.0f} s, {run.turns} turns: {run.result.strip()[:120]}", flush=True)

    stage.check(article)

    return len(jobs), seconds, cost


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
            agents, seconds, cost = run_stage(stage, article)
        except (AgentError, StageError) as exc:
            print(f"\n[{stage.name}] failed: {exc}", file=sys.stderr)
            print(
                f"Rerun from this stage with: python -m pipeline --folder {os.path.relpath(article)} --from {stage.name}",
                file=sys.stderr,
            )
            return 1

        summary.append((stage.name, agents, seconds, cost))
        print(f"[{stage.name}] done", flush=True)

    print(f"\nDone: {article}")

    for name, agents, seconds, cost in summary:
        print(f"  {name:<10} {agents:>3} agent(s)  {seconds:>6.0f} s  ${cost:.4f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
