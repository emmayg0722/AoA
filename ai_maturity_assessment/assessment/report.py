"""Report generator: produces Markdown assessment reports."""

from __future__ import annotations

import datetime
from textwrap import dedent

from .model import DIMENSIONS, LEVEL_CRITERIA, LEVEL_DESCRIPTIONS, MaturityLevel
from .scoring import DimensionScore, OverallResult, get_gap_analysis, get_level_label


def _bar(score: float, max_val: float = 5.0, width: int = 20) -> str:
    filled = int(round(score / max_val * width))
    return "█" * filled + "░" * (width - filled)


def _radar_text(dimension_scores: list[DimensionScore], width: int = 50) -> str:
    lines = []
    max_name_len = max(len(f"{ds.dimension_name_en}") for ds in dimension_scores)
    for ds in dimension_scores:
        name = f"{ds.dimension_name_en}"
        pad = " " * (max_name_len - len(name) + 2)
        bar = _bar(ds.raw_score)
        lines.append(f"  {name}{pad}{bar}  {ds.raw_score:.1f}/5.0")
    return "\n".join(lines)


def _recommendations_for_dimension(ds: DimensionScore) -> list[str]:
    """Generate level-appropriate recommendations."""
    recs = {
        "strategy": {
            1: [
                "Develop a formal AI strategy document aligned with business objectives",
                "Identify an executive sponsor for AI initiatives",
                "Conduct use case discovery workshops across business units",
            ],
            2: [
                "Formalize AI strategy with measurable KPIs and milestones",
                "Establish dedicated AI budget with ROI tracking mechanisms",
                "Create a prioritized AI use case portfolio",
            ],
            3: [
                "Integrate AI strategy into enterprise strategic planning cycle",
                "Establish C-level AI ownership (CAIO or equivalent)",
                "Implement portfolio-level AI investment management",
            ],
            4: [
                "Evolve toward AI-first business model thinking",
                "Establish board-level AI governance and reporting",
                "Drive industry thought leadership in AI strategy",
            ],
        },
        "data": {
            1: [
                "Conduct a comprehensive data audit and create a data inventory",
                "Establish basic data quality standards and ownership",
                "Begin cloud migration planning for AI workloads",
            ],
            2: [
                "Build a centralized data platform (data lake/warehouse)",
                "Implement data quality monitoring and automated checks",
                "Develop a data governance framework with stewards",
            ],
            3: [
                "Evolve to data mesh/fabric architecture for scalability",
                "Implement automated data pipelines with lineage tracking",
                "Adopt privacy-preserving techniques for sensitive AI use cases",
            ],
            4: [
                "Enable real-time streaming data for AI applications",
                "Implement self-service data platforms with governance guardrails",
                "Optimize data infrastructure for auto-scaling and cost efficiency",
            ],
        },
        "technology": {
            1: [
                "Select and standardize an AI/ML development platform",
                "Establish basic model version control and experiment tracking",
                "Define integration patterns for AI services",
            ],
            2: [
                "Implement a model registry with versioning",
                "Develop standardized evaluation benchmarks and test suites",
                "Establish approved GenAI tools with usage guidelines",
            ],
            3: [
                "Build enterprise AI platform with multi-tenant capabilities",
                "Implement RAG pipelines and agentic AI workflows",
                "Deploy comprehensive AI security program with red-teaming",
            ],
            4: [
                "Evolve to composable AI architecture with self-optimization",
                "Pioneer cutting-edge techniques (multimodal AI, foundation models)",
                "Establish platform engineering team for AI golden paths",
            ],
        },
        "talent": {
            1: [
                "Hire initial AI/ML team (data scientists, ML engineers)",
                "Launch basic AI literacy program for all employees",
                "Identify internal AI champions in each business unit",
            ],
            2: [
                "Establish dedicated AI/ML team with defined roles and career paths",
                "Implement structured AI training programs by role",
                "Create cross-functional AI project teams",
            ],
            3: [
                "Establish AI Center of Excellence (CoE) with clear mandate",
                "Embed AI champions across all business units",
                "Build university partnerships for AI talent pipeline",
            ],
            4: [
                "Distribute AI capabilities across all teams",
                "Establish continuous learning culture with quarterly skill refreshes",
                "Build industry-leading AI employer brand",
            ],
        },
        "governance": {
            1: [
                "Develop basic AI usage guidelines and policies",
                "Raise awareness of AI risks across the organization",
                "Begin mapping applicable AI regulations",
            ],
            2: [
                "Establish formal AI governance framework and committee",
                "Implement bias testing for production models",
                "Start compliance mapping (NIST AI RMF / EU AI Act)",
            ],
            3: [
                "Activate AI governance committee with enforcement authority",
                "Automate bias detection and monitoring in production",
                "Achieve full compliance with applicable regulations",
            ],
            4: [
                "Establish industry-leading responsible AI practices",
                "Engage proactively with regulators and standard bodies",
                "Implement transparent AI audit trails enterprise-wide",
            ],
        },
        "operations": {
            1: [
                "Deploy first AI model to production with basic monitoring",
                "Document manual deployment and operations processes",
                "Define SLAs for AI systems",
            ],
            2: [
                "Implement semi-automated CI/CD pipeline for ML models",
                "Set up model performance monitoring with drift detection",
                "Create operational runbooks and incident response procedures",
            ],
            3: [
                "Build fully automated MLOps pipeline",
                "Implement proactive retraining with canary deployments",
                "Establish FinOps practices for AI cost optimization",
            ],
            4: [
                "Evolve to self-healing AI systems with autonomous operations",
                "Implement real-time optimization across model fleet",
                "Achieve industry-leading operational efficiency",
            ],
        },
    }

    level = min(ds.level.value, 4)
    return recs.get(ds.dimension_id, {}).get(level, [
        "Continue current trajectory and benchmark against industry leaders",
    ])


def generate_report(
    result: OverallResult,
    company_name: str = "Assessment Target",
    industry: str = "General",
    assessor: str = "AI Architect (Consulting)",
    target_level: int = 4,
) -> str:
    """Generate a full Markdown assessment report."""
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    level_info = LEVEL_DESCRIPTIONS[result.overall_level]

    sections = []

    # --- Header ---
    sections.append(dedent(f"""\
    # AI Maturity Assessment Report
    # AI 成熟度评估报告

    | Field | Value |
    |-------|-------|
    | **Company / 企业** | {company_name} |
    | **Industry / 行业** | {industry} |
    | **Assessment Date / 评估日期** | {now} |
    | **Assessor / 评估师** | {assessor} |
    | **Assessment Mode / 评估模式** | {"Core (快速评估)" if result.assessment_mode == "core" else "Comprehensive (全面评估)"} |
    | **Questions Answered / 回答问题数** | {result.total_questions} |

    ---
    """))

    # --- Executive Summary ---
    sections.append(dedent(f"""\
    ## Executive Summary / 执行摘要

    ### Overall Maturity Score / 整体成熟度评分

    ```
    Score: {result.overall_score:.1f} / 5.0
    Level: {level_info['en']} ({level_info['zh']})
    {_bar(result.overall_score, width=30)}
    ```

    **{level_info['description']}**

    ### Dimension Overview / 维度概览

    ```
    {_radar_text(result.dimension_scores)}
    ```

    ---
    """))

    # --- Dimension Details ---
    sections.append("## Detailed Assessment / 详细评估\n")

    for ds in result.dimension_scores:
        dl = LEVEL_DESCRIPTIONS[ds.level]
        recs = _recommendations_for_dimension(ds)

        criteria_lines = ""
        for lc in LEVEL_CRITERIA:
            if lc.dimension_id == ds.dimension_id and lc.level == ds.level:
                criteria_lines = "\n".join(f"  - {ind}" for ind in lc.indicators)
                break

        rec_lines = "\n".join(f"{i+1}. {r}" for i, r in enumerate(recs))

        sections.append(dedent(f"""\
        ### {ds.dimension_name_en} ({ds.dimension_name_zh})

        | Metric | Value |
        |--------|-------|
        | **Score** | {ds.raw_score:.1f} / 5.0 |
        | **Level** | {dl['en']} ({dl['zh']}) |
        | **Weight** | {ds.weight:.0%} |
        | **Questions** | {ds.question_count} |

        ```
        {_bar(ds.raw_score, width=30)}  {ds.raw_score:.1f}
        ```

        **Current State Indicators / 当前状态指标:**
        {criteria_lines}

        **Recommendations / 建议:**
        {rec_lines}

        ---
        """))

    # --- Gap Analysis ---
    gaps = get_gap_analysis(result, target_level)
    sections.append(dedent(f"""\
    ## Gap Analysis / 差距分析

    Target Level / 目标等级: **Level {target_level} - {LEVEL_DESCRIPTIONS[MaturityLevel(target_level)]['en']} ({LEVEL_DESCRIPTIONS[MaturityLevel(target_level)]['zh']})**

    | Dimension | Current | Target | Gap | Priority |
    |-----------|---------|--------|-----|----------|
    """))
    for g in gaps:
        sections.append(
            f"| {g['dimension_name']} | {g['current_score']:.1f} | {g['target_score']} | {g['gap']:.1f} | {g['priority']} |\n"
        )

    # --- Priority Roadmap ---
    high_gaps = [g for g in gaps if g["priority"] == "High"]
    med_gaps = [g for g in gaps if g["priority"] == "Medium"]
    low_gaps = [g for g in gaps if g["priority"] == "Low"]

    sections.append(dedent(f"""
    ---

    ## Recommended Roadmap / 建议路线图

    ### Phase 1: Foundation (Months 1-3) / 基础阶段
    **Focus: Address critical gaps / 聚焦：解决关键差距**
    """))
    if high_gaps:
        for g in high_gaps:
            dim_id = g["dimension_id"]
            ds_match = next((ds for ds in result.dimension_scores if ds.dimension_id == dim_id), None)
            if ds_match:
                recs = _recommendations_for_dimension(ds_match)
                for r in recs[:2]:
                    sections.append(f"- {r}\n")
    else:
        sections.append("- No critical gaps identified. Focus on medium-priority items.\n")

    sections.append(dedent("""
    ### Phase 2: Acceleration (Months 4-9) / 加速阶段
    **Focus: Close medium gaps, begin scaling / 聚焦：弥合中等差距，开始规模化**
    """))
    if med_gaps:
        for g in med_gaps:
            dim_id = g["dimension_id"]
            ds_match = next((ds for ds in result.dimension_scores if ds.dimension_id == dim_id), None)
            if ds_match:
                recs = _recommendations_for_dimension(ds_match)
                for r in recs[:2]:
                    sections.append(f"- {r}\n")
    else:
        sections.append("- No medium gaps. Focus on optimization.\n")

    sections.append(dedent("""
    ### Phase 3: Optimization (Months 10-18) / 优化阶段
    **Focus: Continuous improvement, reach target maturity / 聚焦：持续改进，达到目标成熟度**
    """))
    if low_gaps:
        for g in low_gaps:
            dim_id = g["dimension_id"]
            ds_match = next((ds for ds in result.dimension_scores if ds.dimension_id == dim_id), None)
            if ds_match:
                recs = _recommendations_for_dimension(ds_match)
                for r in recs[:1]:
                    sections.append(f"- {r}\n")
    sections.append("- Benchmark against industry leaders and refine strategies\n")
    sections.append("- Establish continuous assessment cadence (quarterly reviews)\n")

    # --- Methodology ---
    sections.append(dedent("""
    ---

    ## Methodology / 评估方法

    This assessment is based on a structured maturity model covering 6 dimensions:

    | Dimension | Weight | Description |
    |-----------|--------|-------------|
    """))
    for d in DIMENSIONS:
        sections.append(f"| {d.name_en} ({d.name_zh}) | {d.weight:.0%} | {d.description} |\n")

    sections.append(dedent("""
    **Maturity Levels / 成熟度等级:**

    | Level | Name | Description |
    |-------|------|-------------|
    """))
    for level in MaturityLevel:
        desc = LEVEL_DESCRIPTIONS[level]
        sections.append(f"| {level.value} | {desc['en']} ({desc['zh']}) | {desc['description']} |\n")

    sections.append(dedent("""
    ---

    *This report was generated by the AI Maturity Assessment Agent.*
    *本报告由 AI 成熟度评估 Agent 自动生成。*
    """))

    return "\n".join(sections)
