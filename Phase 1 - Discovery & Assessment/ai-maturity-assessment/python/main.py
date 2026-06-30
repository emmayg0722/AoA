#!/usr/bin/env python3
"""AI Maturity Assessment Agent - Entry Point."""

import argparse
import json
import sys
from pathlib import Path

from assessment.engine import run_assessment
from assessment.questions import get_questions
from assessment.report import generate_report
from assessment.scoring import compute_scores


def cmd_interactive(args):
    """Run interactive assessment."""
    run_assessment()


def cmd_batch(args):
    """Run assessment from a JSON answers file."""
    answers_path = Path(args.answers)
    if not answers_path.exists():
        print(f"Error: file not found: {answers_path}")
        sys.exit(1)

    data = json.loads(answers_path.read_text(encoding="utf-8"))

    answers = data.get("answers", data)
    meta = data.get("metadata", {})
    company = meta.get("company", args.company or "Assessment Target")
    industry = meta.get("industry", args.industry or "General")
    assessor = meta.get("assessor", args.assessor or "AI Architect")
    target = meta.get("target_level", args.target_level or 4)
    mode = meta.get("mode", "comprehensive")

    result = compute_scores(answers, assessment_mode=mode)
    report = generate_report(
        result,
        company_name=company,
        industry=industry,
        assessor=assessor,
        target_level=target,
    )

    output_path = Path(args.output) if args.output else Path("output/assessment_report.md")
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    from assessment.scoring import get_level_label
    print(f"Overall Score: {result.overall_score:.1f} / 5.0")
    print(f"Level: {get_level_label(result.overall_level)}")
    print(f"Report saved to: {output_path}")


def cmd_questions(args):
    """Export question bank."""
    core_only = args.core_only
    questions = get_questions(core_only=core_only)

    if args.format == "json":
        data = [
            {
                "id": q.id,
                "dimension": q.dimension_id,
                "text_en": q.text_en,
                "text_zh": q.text_zh,
                "is_core": q.is_core,
                "options": q.options,
            }
            for q in questions
        ]
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        for q in questions:
            print(f"\n[{q.id}] ({q.dimension_id}) {'[CORE]' if q.is_core else '[DEEP]'}")
            print(f"  EN: {q.text_en}")
            print(f"  ZH: {q.text_zh}")
            for opt in q.options:
                print(f"    {opt['value']}. {opt['text_en']} / {opt['text_zh']}")


def cmd_demo(args):
    """Run a demo assessment with sample answers to show report output."""
    sample_answers = {
        "S1": 2, "S2": 2, "S3": 1, "S4": 2,
        "D1": 3, "D2": 2, "D3": 3, "D4": 2,
        "T1": 2, "T2": 3, "T3": 2, "T4": 1,
        "P1": 2, "P2": 1, "P3": 3,
        "G1": 1, "G2": 2, "G3": 1,
        "O1": 2, "O2": 1, "O3": 1,
    }

    result = compute_scores(sample_answers, assessment_mode="core")
    report = generate_report(
        result,
        company_name="Demo Corp",
        industry="Financial Services",
        assessor="AI Architect (Consulting)",
        target_level=4,
    )

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "demo_assessment_report.md"
    output_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"\n--- Report also saved to: {output_path} ---")


def main():
    parser = argparse.ArgumentParser(
        description="AI Maturity Assessment Agent / AI 成熟度评估工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python main.py                        # Interactive assessment
  python main.py demo                   # Generate demo report
  python main.py questions --format json # Export questions as JSON
  python main.py batch answers.json     # Batch mode from file
        """,
    )
    subparsers = parser.add_subparsers(dest="command")

    # interactive (default)
    sub_interactive = subparsers.add_parser("interactive", help="Run interactive assessment")
    sub_interactive.set_defaults(func=cmd_interactive)

    # demo
    sub_demo = subparsers.add_parser("demo", help="Generate a demo report with sample data")
    sub_demo.set_defaults(func=cmd_demo)

    # questions
    sub_questions = subparsers.add_parser("questions", help="Export question bank")
    sub_questions.add_argument("--format", choices=["text", "json"], default="text")
    sub_questions.add_argument("--core-only", action="store_true")
    sub_questions.set_defaults(func=cmd_questions)

    # batch
    sub_batch = subparsers.add_parser("batch", help="Run assessment from answers file")
    sub_batch.add_argument("answers", help="Path to JSON file with answers")
    sub_batch.add_argument("--output", "-o", help="Output report path")
    sub_batch.add_argument("--company", help="Company name")
    sub_batch.add_argument("--industry", help="Industry")
    sub_batch.add_argument("--assessor", help="Assessor name")
    sub_batch.add_argument("--target-level", type=int, default=4)
    sub_batch.set_defaults(func=cmd_batch)

    args = parser.parse_args()

    if args.command is None:
        cmd_interactive(args)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
