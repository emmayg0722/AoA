"""Interactive assessment engine: drives the CLI questionnaire."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .model import DIMENSIONS
from .questions import Question, get_questions
from .report import generate_report
from .scoring import OverallResult, compute_scores


def _print_header():
    print("\n" + "=" * 60)
    print("  AI Maturity Assessment Agent")
    print("  AI 成熟度评估工具")
    print("=" * 60)


def _ask_text(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"\n{prompt}{suffix}: ").strip()
    return val if val else default


def _ask_choice(prompt: str, options: list[str], default: int = 1) -> int:
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        marker = " *" if i == default else ""
        print(f"  {i}. {opt}{marker}")
    while True:
        raw = input(f"\nYour choice / 请选择 [1-{len(options)}]: ").strip()
        if not raw:
            return default
        try:
            choice = int(raw)
            if 1 <= choice <= len(options):
                return choice
        except ValueError:
            pass
        print(f"  Please enter a number between 1 and {len(options)}.")


def _ask_question(q: Question, index: int, total: int) -> int:
    print(f"\n{'─' * 50}")
    print(f"  Question {index}/{total}  [{q.dimension_id.upper()}]")
    print(f"{'─' * 50}")
    print(f"\n  {q.text_en}")
    print(f"  {q.text_zh}")
    print()
    for opt in q.options:
        print(f"  {opt['value']}. {opt['text_en']}")
        print(f"     {opt['text_zh']}")
    print()

    while True:
        raw = input("  Your answer / 请选择 (1-5): ").strip()
        try:
            val = int(raw)
            if 1 <= val <= 5:
                return val
        except ValueError:
            pass
        print("  Please enter a number between 1 and 5.")


def run_assessment():
    """Run the interactive assessment."""
    _print_header()

    # --- Collect metadata ---
    company = _ask_text("Company name / 企业名称", "My Company")
    industry = _ask_text("Industry / 行业", "Technology")
    assessor = _ask_text("Assessor name / 评估师", "AI Architect")

    mode_choice = _ask_choice(
        "Assessment mode / 评估模式:",
        [
            "Core (Quick ~20 questions, 10 min) / 核心评估（约20题，10分钟）",
            "Comprehensive (All ~33 questions, 20 min) / 全面评估（约33题，20分钟）",
        ],
        default=1,
    )
    core_only = mode_choice == 1
    mode_label = "core" if core_only else "comprehensive"

    target_level = _ask_choice(
        "Target maturity level / 目标成熟度等级:",
        [
            "Level 3 - Operationalizing (运营化)",
            "Level 4 - Scaling (规模化) [Recommended]",
            "Level 5 - Transforming (转型期)",
        ],
        default=2,
    )
    target = target_level + 2  # map 1->3, 2->4, 3->5

    # --- Run questions ---
    questions = get_questions(core_only=core_only)
    total = len(questions)

    print(f"\n{'=' * 60}")
    print(f"  Starting assessment: {total} questions")
    print(f"  开始评估：共 {total} 个问题")
    print(f"{'=' * 60}")
    print("  Tip: For each question, select the option (1-5) that")
    print("  best describes your organization's CURRENT state.")
    print("  提示：每道题请选择最符合贵组织当前状态的选项（1-5）。")

    answers: dict[str, int] = {}
    current_dim = ""

    for i, q in enumerate(questions, 1):
        if q.dimension_id != current_dim:
            current_dim = q.dimension_id
            dim = next(d for d in DIMENSIONS if d.id == current_dim)
            print(f"\n\n{'━' * 60}")
            print(f"  📊 {dim.name_en} / {dim.name_zh}")
            print(f"  {dim.description}")
            print(f"{'━' * 60}")

        answers[q.id] = _ask_question(q, i, total)

    # --- Compute & generate ---
    print(f"\n\n{'=' * 60}")
    print("  Computing results... / 正在计算结果...")
    print(f"{'=' * 60}")

    result = compute_scores(answers, assessment_mode=mode_label)
    report = generate_report(
        result,
        company_name=company,
        industry=industry,
        assessor=assessor,
        target_level=target,
    )

    # --- Save outputs ---
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_company = company.replace(" ", "_").replace("/", "_")

    report_path = output_dir / f"assessment_{safe_company}_{timestamp}.md"
    report_path.write_text(report, encoding="utf-8")

    data_path = output_dir / f"assessment_{safe_company}_{timestamp}.json"
    data = {
        "metadata": {
            "company": company,
            "industry": industry,
            "assessor": assessor,
            "mode": mode_label,
            "target_level": target,
            "total_questions": result.total_questions,
        },
        "answers": answers,
        "scores": {
            "overall_score": result.overall_score,
            "overall_level": result.overall_level.value,
            "dimensions": [
                {
                    "id": ds.dimension_id,
                    "name": ds.dimension_name_en,
                    "score": ds.raw_score,
                    "level": ds.level.value,
                    "weight": ds.weight,
                }
                for ds in result.dimension_scores
            ],
        },
    }
    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # --- Print summary ---
    from .scoring import get_level_label
    print(f"\n{'=' * 60}")
    print("  ASSESSMENT COMPLETE / 评估完成")
    print(f"{'=' * 60}")
    print(f"\n  Overall Score: {result.overall_score:.1f} / 5.0")
    print(f"  Maturity Level: {get_level_label(result.overall_level)}")
    print()
    for ds in result.dimension_scores:
        bar = "█" * int(round(ds.raw_score / 5.0 * 15)) + "░" * (15 - int(round(ds.raw_score / 5.0 * 15)))
        print(f"  {ds.dimension_name_en:25s} {bar}  {ds.raw_score:.1f}")
    print()
    print(f"  Report saved to: {report_path}")
    print(f"  Data saved to:   {data_path}")
    print(f"{'=' * 60}\n")

    return result, str(report_path)
