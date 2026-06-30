"""Scoring engine: computes per-dimension and overall maturity scores."""

from __future__ import annotations

from dataclasses import dataclass

from .model import DIMENSIONS, LEVEL_DESCRIPTIONS, MaturityLevel


@dataclass
class DimensionScore:
    dimension_id: str
    dimension_name_en: str
    dimension_name_zh: str
    raw_score: float       # average of question scores (1.0 - 5.0)
    weighted_score: float  # raw_score * weight
    weight: float
    level: MaturityLevel
    question_count: int
    answers: dict[str, int]  # question_id -> chosen value


@dataclass
class OverallResult:
    overall_score: float         # weighted average (1.0 - 5.0)
    overall_level: MaturityLevel
    dimension_scores: list[DimensionScore]
    total_questions: int
    assessment_mode: str         # "core" or "comprehensive"


def _score_to_level(score: float) -> MaturityLevel:
    if score < 1.5:
        return MaturityLevel.EXPLORING
    elif score < 2.5:
        return MaturityLevel.EXPERIMENTING
    elif score < 3.5:
        return MaturityLevel.OPERATIONALIZING
    elif score < 4.5:
        return MaturityLevel.SCALING
    else:
        return MaturityLevel.TRANSFORMING


def compute_scores(answers: dict[str, int], assessment_mode: str = "core") -> OverallResult:
    """
    Compute maturity scores from answers.

    Args:
        answers: dict mapping question_id -> chosen value (1-5)
        assessment_mode: "core" or "comprehensive"

    Returns:
        OverallResult with per-dimension and overall scores.
    """
    dim_lookup = {d.id: d for d in DIMENSIONS}
    dim_answers: dict[str, dict[str, int]] = {d.id: {} for d in DIMENSIONS}

    for qid, value in answers.items():
        prefix_map = {"S": "strategy", "D": "data", "T": "technology",
                      "P": "talent", "G": "governance", "O": "operations"}
        dim_id = prefix_map.get(qid[0])
        if dim_id:
            dim_answers[dim_id][qid] = value

    dimension_scores: list[DimensionScore] = []
    for dim in DIMENSIONS:
        ans = dim_answers[dim.id]
        if not ans:
            raw = 0.0
        else:
            raw = sum(ans.values()) / len(ans)

        dimension_scores.append(DimensionScore(
            dimension_id=dim.id,
            dimension_name_en=dim.name_en,
            dimension_name_zh=dim.name_zh,
            raw_score=round(raw, 2),
            weighted_score=round(raw * dim.weight, 2),
            weight=dim.weight,
            level=_score_to_level(raw),
            question_count=len(ans),
            answers=ans,
        ))

    overall = sum(ds.weighted_score for ds in dimension_scores)
    overall_score = round(overall / sum(d.weight for d in DIMENSIONS), 2) if DIMENSIONS else 0

    return OverallResult(
        overall_score=overall_score,
        overall_level=_score_to_level(overall_score),
        dimension_scores=dimension_scores,
        total_questions=len(answers),
        assessment_mode=assessment_mode,
    )


def get_level_label(level: MaturityLevel) -> str:
    desc = LEVEL_DESCRIPTIONS[level]
    return f"Level {level.value}: {desc['en']} ({desc['zh']})"


def get_gap_analysis(result: OverallResult, target_level: int = 4) -> list[dict]:
    """Identify gaps between current scores and target level."""
    gaps = []
    for ds in result.dimension_scores:
        gap = target_level - ds.raw_score
        if gap > 0:
            gaps.append({
                "dimension_id": ds.dimension_id,
                "dimension_name": f"{ds.dimension_name_en} ({ds.dimension_name_zh})",
                "current_score": ds.raw_score,
                "current_level": get_level_label(ds.level),
                "target_score": target_level,
                "gap": round(gap, 2),
                "priority": "High" if gap >= 2.0 else ("Medium" if gap >= 1.0 else "Low"),
            })
    gaps.sort(key=lambda g: g["gap"], reverse=True)
    return gaps
