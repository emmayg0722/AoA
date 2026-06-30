"""AI Maturity Model definitions: levels, dimensions, and scoring criteria."""

from dataclasses import dataclass, field
from enum import IntEnum


class MaturityLevel(IntEnum):
    EXPLORING = 1       # 探索期
    EXPERIMENTING = 2   # 实验期
    OPERATIONALIZING = 3  # 运营化
    SCALING = 4         # 规模化
    TRANSFORMING = 5    # 转型期


LEVEL_DESCRIPTIONS = {
    MaturityLevel.EXPLORING: {
        "en": "Exploring",
        "zh": "探索期",
        "description": "Ad-hoc AI initiatives, no formal strategy. Awareness exists but adoption is minimal.",
    },
    MaturityLevel.EXPERIMENTING: {
        "en": "Experimenting",
        "zh": "实验期",
        "description": "Isolated pilots and PoCs. Some dedicated resources but limited governance and scalability.",
    },
    MaturityLevel.OPERATIONALIZING: {
        "en": "Operationalizing",
        "zh": "运营化",
        "description": "AI in production for select use cases. Defined processes, MLOps basics, emerging governance.",
    },
    MaturityLevel.SCALING: {
        "en": "Scaling",
        "zh": "规模化",
        "description": "Enterprise-wide AI adoption. Mature MLOps, governance framework, and cross-functional collaboration.",
    },
    MaturityLevel.TRANSFORMING: {
        "en": "Transforming",
        "zh": "转型期",
        "description": "AI-first culture. Continuous innovation, advanced governance, measurable business transformation.",
    },
}


@dataclass
class Dimension:
    id: str
    name_en: str
    name_zh: str
    description: str
    weight: float  # 0.0 - 1.0, all dimensions sum to 1.0


DIMENSIONS = [
    Dimension(
        id="strategy",
        name_en="Strategy & Vision",
        name_zh="战略与愿景",
        description="Executive sponsorship, AI strategy alignment with business goals, investment commitment, and innovation roadmap.",
        weight=0.20,
    ),
    Dimension(
        id="data",
        name_en="Data & Infrastructure",
        name_zh="数据与基础设施",
        description="Data quality, availability, governance, infrastructure readiness, and cloud/compute capabilities.",
        weight=0.20,
    ),
    Dimension(
        id="technology",
        name_en="Technology & Architecture",
        name_zh="技术与架构",
        description="AI/ML platforms, model development practices, integration architecture, and technology stack maturity.",
        weight=0.18,
    ),
    Dimension(
        id="talent",
        name_en="Talent & Organization",
        name_zh="人才与组织",
        description="AI skills, team structure, training programs, organizational culture, and change readiness.",
        weight=0.15,
    ),
    Dimension(
        id="governance",
        name_en="Governance & Ethics",
        name_zh="治理与伦理",
        description="AI policies, responsible AI practices, compliance readiness, risk management, and audit capabilities.",
        weight=0.15,
    ),
    Dimension(
        id="operations",
        name_en="Operations & Scale",
        name_zh="运营与规模化",
        description="MLOps maturity, model monitoring, CI/CD for ML, production reliability, and scaling capabilities.",
        weight=0.12,
    ),
]


@dataclass
class LevelCriteria:
    """Per-dimension criteria describing what each maturity level looks like."""
    dimension_id: str
    level: MaturityLevel
    indicators: list[str]


LEVEL_CRITERIA: list[LevelCriteria] = [
    # --- Strategy & Vision ---
    LevelCriteria("strategy", MaturityLevel.EXPLORING, [
        "No formal AI strategy",
        "AI interest driven by individuals, not leadership",
        "No dedicated AI budget",
    ]),
    LevelCriteria("strategy", MaturityLevel.EXPERIMENTING, [
        "Initial AI strategy drafted",
        "Some executive awareness",
        "Ad-hoc budget allocated for pilots",
    ]),
    LevelCriteria("strategy", MaturityLevel.OPERATIONALIZING, [
        "Documented AI strategy aligned with business goals",
        "Executive sponsor identified",
        "Dedicated AI budget with ROI tracking",
    ]),
    LevelCriteria("strategy", MaturityLevel.SCALING, [
        "AI embedded in enterprise strategy",
        "C-level ownership (CAIO or equivalent)",
        "Portfolio-level AI investment management",
    ]),
    LevelCriteria("strategy", MaturityLevel.TRANSFORMING, [
        "AI-first business model",
        "Board-level AI governance",
        "AI drives competitive differentiation",
    ]),
    # --- Data & Infrastructure ---
    LevelCriteria("data", MaturityLevel.EXPLORING, [
        "Data siloed across departments",
        "No data quality standards",
        "Limited cloud infrastructure",
    ]),
    LevelCriteria("data", MaturityLevel.EXPERIMENTING, [
        "Some data consolidation efforts",
        "Basic data quality checks",
        "Initial cloud migration",
    ]),
    LevelCriteria("data", MaturityLevel.OPERATIONALIZING, [
        "Centralized data platform (lake/warehouse)",
        "Data quality monitoring in place",
        "Cloud-native AI infrastructure",
    ]),
    LevelCriteria("data", MaturityLevel.SCALING, [
        "Enterprise data mesh/fabric",
        "Automated data quality pipelines",
        "Multi-cloud or hybrid strategy",
    ]),
    LevelCriteria("data", MaturityLevel.TRANSFORMING, [
        "Real-time data streams powering AI",
        "Self-service data with governance guardrails",
        "Infrastructure auto-scales with demand",
    ]),
    # --- Technology & Architecture ---
    LevelCriteria("technology", MaturityLevel.EXPLORING, [
        "No standardized AI tools",
        "Individual experimentation with notebooks",
        "No integration architecture",
    ]),
    LevelCriteria("technology", MaturityLevel.EXPERIMENTING, [
        "Some AI/ML tools adopted",
        "Basic model development workflow",
        "Point-to-point integrations",
    ]),
    LevelCriteria("technology", MaturityLevel.OPERATIONALIZING, [
        "Standardized ML platform",
        "Model registry and versioning",
        "API-based integration architecture",
    ]),
    LevelCriteria("technology", MaturityLevel.SCALING, [
        "Enterprise AI platform with multi-tenant support",
        "Agentic AI and RAG capabilities",
        "Event-driven architecture",
    ]),
    LevelCriteria("technology", MaturityLevel.TRANSFORMING, [
        "Composable AI architecture",
        "Self-optimizing systems",
        "Cutting-edge adoption (foundation models, multimodal AI)",
    ]),
    # --- Talent & Organization ---
    LevelCriteria("talent", MaturityLevel.EXPLORING, [
        "No dedicated AI roles",
        "AI interest from a few individuals",
        "No AI training programs",
    ]),
    LevelCriteria("talent", MaturityLevel.EXPERIMENTING, [
        "Small AI team or data scientists hired",
        "Basic AI literacy awareness",
        "Ad-hoc learning initiatives",
    ]),
    LevelCriteria("talent", MaturityLevel.OPERATIONALIZING, [
        "Dedicated AI/ML team",
        "Structured training programs",
        "Cross-functional AI collaboration",
    ]),
    LevelCriteria("talent", MaturityLevel.SCALING, [
        "AI CoE (Center of Excellence) established",
        "AI literacy across business units",
        "Embedded AI champions in each department",
    ]),
    LevelCriteria("talent", MaturityLevel.TRANSFORMING, [
        "AI skills embedded in all roles",
        "Continuous learning culture",
        "Industry-leading AI talent brand",
    ]),
    # --- Governance & Ethics ---
    LevelCriteria("governance", MaturityLevel.EXPLORING, [
        "No AI policies or guidelines",
        "No awareness of AI risks",
        "No compliance considerations",
    ]),
    LevelCriteria("governance", MaturityLevel.EXPERIMENTING, [
        "Basic AI usage guidelines",
        "Awareness of responsible AI concepts",
        "Initial risk assessment for pilots",
    ]),
    LevelCriteria("governance", MaturityLevel.OPERATIONALIZING, [
        "Formal AI governance framework",
        "Bias testing for production models",
        "Compliance mapping started (NIST/EU AI Act)",
    ]),
    LevelCriteria("governance", MaturityLevel.SCALING, [
        "AI governance committee active",
        "Automated bias detection and monitoring",
        "Full compliance with relevant regulations",
    ]),
    LevelCriteria("governance", MaturityLevel.TRANSFORMING, [
        "Industry-leading responsible AI practices",
        "Proactive regulatory engagement",
        "Transparent AI audit trails enterprise-wide",
    ]),
    # --- Operations & Scale ---
    LevelCriteria("operations", MaturityLevel.EXPLORING, [
        "No models in production",
        "Manual, ad-hoc processes",
        "No monitoring or alerting",
    ]),
    LevelCriteria("operations", MaturityLevel.EXPERIMENTING, [
        "1-2 models in production",
        "Manual deployment process",
        "Basic monitoring (uptime only)",
    ]),
    LevelCriteria("operations", MaturityLevel.OPERATIONALIZING, [
        "Multiple models in production",
        "Semi-automated CI/CD for ML",
        "Model performance monitoring and drift detection",
    ]),
    LevelCriteria("operations", MaturityLevel.SCALING, [
        "Dozens of models in production",
        "Fully automated MLOps pipeline",
        "Proactive retraining and canary deployments",
    ]),
    LevelCriteria("operations", MaturityLevel.TRANSFORMING, [
        "Hundreds of models, self-healing systems",
        "Autonomous MLOps with human oversight",
        "Real-time optimization across model fleet",
    ]),
]
