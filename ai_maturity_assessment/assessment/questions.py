"""Question bank for AI Maturity Assessment, organized by dimension."""

from dataclasses import dataclass


@dataclass
class Question:
    id: str
    dimension_id: str
    text_en: str
    text_zh: str
    options: list[dict]  # each dict has: value (1-5), text_en, text_zh
    is_core: bool = True  # core questions shown in quick assessment


def _make_options(texts: list[tuple[str, str]]) -> list[dict]:
    """Helper to create option list from (en, zh) tuples, scored 1-5."""
    return [
        {"value": i + 1, "text_en": en, "text_zh": zh}
        for i, (en, zh) in enumerate(texts)
    ]


QUESTIONS: list[Question] = [
    # =========================================================================
    # STRATEGY & VISION (战略与愿景) — 6 questions (4 core + 2 deep)
    # =========================================================================
    Question(
        id="S1", dimension_id="strategy", is_core=True,
        text_en="How would you describe your organization's AI strategy?",
        text_zh="您如何描述贵组织的 AI 战略？",
        options=_make_options([
            ("No AI strategy exists", "没有 AI 战略"),
            ("Informal discussions about AI potential", "对 AI 潜力有非正式讨论"),
            ("Documented AI strategy aligned with business goals", "已制定与业务目标对齐的 AI 战略文档"),
            ("AI strategy integrated into enterprise strategy with KPIs", "AI 战略已融入企业战略并有 KPI 跟踪"),
            ("AI is a core pillar of business model and competitive strategy", "AI 是商业模式和竞争战略的核心支柱"),
        ]),
    ),
    Question(
        id="S2", dimension_id="strategy", is_core=True,
        text_en="What level of executive sponsorship does AI have?",
        text_zh="AI 获得了什么级别的高管支持？",
        options=_make_options([
            ("No executive sponsor", "没有高管支持"),
            ("Mid-level management interest", "中层管理者有兴趣"),
            ("Senior executive sponsor identified", "已确定高级管理层支持者"),
            ("C-suite ownership (CTO/CDO/CAIO)", "C 级高管负责（CTO/CDO/CAIO）"),
            ("Board-level AI governance and oversight", "董事会级别的 AI 治理与监督"),
        ]),
    ),
    Question(
        id="S3", dimension_id="strategy", is_core=True,
        text_en="How is AI investment managed in your organization?",
        text_zh="贵组织如何管理 AI 投资？",
        options=_make_options([
            ("No dedicated AI budget", "没有专门的 AI 预算"),
            ("Ad-hoc funding for individual projects", "为个别项目提供临时资金"),
            ("Dedicated annual AI budget with project-level tracking", "有专门年度 AI 预算并按项目跟踪"),
            ("Portfolio-level AI investment with ROI measurement", "组合级别的 AI 投资并衡量 ROI"),
            ("Strategic AI investment fund with innovation allocation", "战略性 AI 投资基金，含创新投入"),
        ]),
    ),
    Question(
        id="S4", dimension_id="strategy", is_core=True,
        text_en="How many AI use cases have been identified and prioritized?",
        text_zh="已识别并排序了多少个 AI 用例？",
        options=_make_options([
            ("None formally identified", "没有正式识别"),
            ("A few ideas discussed informally", "有一些非正式讨论的想法"),
            ("5-10 use cases documented and prioritized", "已记录并排序 5-10 个用例"),
            ("Comprehensive use case portfolio across business units", "跨业务单元的全面用例组合"),
            ("Continuously evolving pipeline with business impact scoring", "持续演进的用例管道，有业务影响评分"),
        ]),
    ),
    Question(
        id="S5", dimension_id="strategy", is_core=False,
        text_en="Does your organization have an AI innovation roadmap?",
        text_zh="贵组织是否有 AI 创新路线图？",
        options=_make_options([
            ("No roadmap exists", "没有路线图"),
            ("Informal plans for next quarter", "下季度的非正式计划"),
            ("12-month roadmap with milestones", "12 个月路线图，有里程碑"),
            ("3-year roadmap updated quarterly", "3 年路线图，每季度更新"),
            ("5-year vision with adaptive roadmap and emerging tech tracking", "5 年愿景，自适应路线图并跟踪新兴技术"),
        ]),
    ),
    Question(
        id="S6", dimension_id="strategy", is_core=False,
        text_en="How does your organization benchmark AI progress?",
        text_zh="贵组织如何衡量 AI 进展？",
        options=_make_options([
            ("No benchmarking", "没有衡量"),
            ("Informal comparison with competitors", "与竞争对手的非正式比较"),
            ("Internal KPIs for AI projects", "AI 项目的内部 KPI"),
            ("Industry benchmarking with external assessments", "通过外部评估进行行业对标"),
            ("Continuous benchmarking driving strategic decisions", "持续对标驱动战略决策"),
        ]),
    ),

    # =========================================================================
    # DATA & INFRASTRUCTURE (数据与基础设施) — 6 questions (4 core + 2 deep)
    # =========================================================================
    Question(
        id="D1", dimension_id="data", is_core=True,
        text_en="How would you describe your organization's data quality and availability?",
        text_zh="您如何描述贵组织的数据质量和可用性？",
        options=_make_options([
            ("Data is siloed, inconsistent, and hard to access", "数据孤立、不一致且难以访问"),
            ("Some data consolidated but quality varies significantly", "部分数据已整合但质量差异显著"),
            ("Centralized data platform with quality monitoring", "有集中数据平台并进行质量监控"),
            ("Enterprise data mesh/fabric with automated quality pipelines", "企业数据网格/织物，自动化质量管道"),
            ("Real-time, self-service data with governance guardrails", "实时、自助式数据，有治理护栏"),
        ]),
    ),
    Question(
        id="D2", dimension_id="data", is_core=True,
        text_en="What is the state of your data governance?",
        text_zh="贵组织的数据治理现状如何？",
        options=_make_options([
            ("No formal data governance", "没有正式数据治理"),
            ("Basic data ownership defined for some datasets", "部分数据集定义了基本数据所有权"),
            ("Data governance framework with policies and stewards", "有数据治理框架、政策和管理员"),
            ("Automated data governance with lineage tracking", "自动化数据治理，有血缘追踪"),
            ("Self-governing data ecosystem with AI-driven quality", "自治数据生态系统，AI 驱动质量管控"),
        ]),
    ),
    Question(
        id="D3", dimension_id="data", is_core=True,
        text_en="How mature is your cloud/compute infrastructure for AI workloads?",
        text_zh="贵组织用于 AI 工作负载的云/计算基础设施成熟度如何？",
        options=_make_options([
            ("On-premises only, no GPU/TPU access", "仅本地部署，无 GPU/TPU 访问"),
            ("Initial cloud adoption, limited AI-specific resources", "初步采用云，有限的 AI 专用资源"),
            ("Cloud-native AI infrastructure with managed ML services", "云原生 AI 基础设施，有托管 ML 服务"),
            ("Multi-cloud/hybrid with auto-scaling for AI workloads", "多云/混合，AI 工作负载自动扩缩"),
            ("Optimized infrastructure with cost management and edge AI", "优化基础设施，成本管理和边缘 AI"),
        ]),
    ),
    Question(
        id="D4", dimension_id="data", is_core=True,
        text_en="How is data prepared and managed for AI/ML use cases?",
        text_zh="数据如何为 AI/ML 用例进行准备和管理？",
        options=_make_options([
            ("Manual, ad-hoc data preparation", "手动、临时数据准备"),
            ("Some scripted data pipelines for specific projects", "为特定项目编写了一些数据管道脚本"),
            ("Standardized ETL/ELT pipelines with feature stores", "标准化 ETL/ELT 管道，有特征存储"),
            ("Automated data pipelines with versioning and lineage", "自动化数据管道，有版本控制和血缘追踪"),
            ("Real-time streaming pipelines with self-service feature engineering", "实时流式管道，自助特征工程"),
        ]),
    ),
    Question(
        id="D5", dimension_id="data", is_core=False,
        text_en="How does your organization handle data privacy and security for AI?",
        text_zh="贵组织如何处理 AI 的数据隐私和安全？",
        options=_make_options([
            ("No specific AI data privacy measures", "没有特定的 AI 数据隐私措施"),
            ("Basic access controls, privacy handled case-by-case", "基本访问控制，隐私逐案处理"),
            ("Data classification and encryption for AI datasets", "AI 数据集的数据分类和加密"),
            ("Privacy-preserving techniques (anonymization, differential privacy)", "隐私保护技术（匿名化、差分隐私）"),
            ("Federated learning and advanced privacy-by-design", "联邦学习和高级隐私设计"),
        ]),
    ),
    Question(
        id="D6", dimension_id="data", is_core=False,
        text_en="How well can your organization integrate external data sources for AI?",
        text_zh="贵组织整合外部数据源用于 AI 的能力如何？",
        options=_make_options([
            ("No external data integration", "没有外部数据整合"),
            ("Manual import of external datasets", "手动导入外部数据集"),
            ("API-based integration with select external sources", "与部分外部数据源基于 API 集成"),
            ("Automated ingestion from multiple external sources", "从多个外部数据源自动采集"),
            ("Real-time external data enrichment with quality validation", "实时外部数据增强，有质量验证"),
        ]),
    ),

    # =========================================================================
    # TECHNOLOGY & ARCHITECTURE (技术与架构) — 6 questions (4 core + 2 deep)
    # =========================================================================
    Question(
        id="T1", dimension_id="technology", is_core=True,
        text_en="What is the state of your AI/ML development platform?",
        text_zh="贵组织的 AI/ML 开发平台现状如何？",
        options=_make_options([
            ("No standardized tools; individuals use local notebooks", "没有标准化工具；个人使用本地 notebook"),
            ("Some shared tools but no unified platform", "有一些共享工具但没有统一平台"),
            ("Standardized ML platform with experiment tracking", "标准化 ML 平台，有实验追踪"),
            ("Enterprise AI platform with multi-tenant support and model registry", "企业 AI 平台，多租户支持和模型注册表"),
            ("Composable AI platform with auto-optimization and self-service", "可组合 AI 平台，自动优化和自助服务"),
        ]),
    ),
    Question(
        id="T2", dimension_id="technology", is_core=True,
        text_en="How does your organization use Generative AI / LLMs?",
        text_zh="贵组织如何使用生成式 AI / 大语言模型？",
        options=_make_options([
            ("No GenAI usage", "没有使用生成式 AI"),
            ("Individual experimentation with ChatGPT/similar tools", "个人使用 ChatGPT 等工具进行实验"),
            ("Approved GenAI tools with usage guidelines", "已批准的 GenAI 工具并有使用指南"),
            ("Custom RAG pipelines and fine-tuned models in production", "自定义 RAG 管道和微调模型已投产"),
            ("Agentic AI workflows with multimodal capabilities in production", "Agentic AI 工作流和多模态能力已投产"),
        ]),
    ),
    Question(
        id="T3", dimension_id="technology", is_core=True,
        text_en="How mature is your AI integration architecture?",
        text_zh="贵组织的 AI 集成架构成熟度如何？",
        options=_make_options([
            ("No integration; AI exists in isolated experiments", "没有集成；AI 存在于独立实验中"),
            ("Point-to-point integrations for specific projects", "为特定项目进行点对点集成"),
            ("API-based microservices architecture for AI", "基于 API 的微服务架构用于 AI"),
            ("Event-driven architecture with AI service orchestration", "事件驱动架构，AI 服务编排"),
            ("Composable, self-healing AI services with autonomous scaling", "可组合、自愈的 AI 服务，自主扩缩"),
        ]),
    ),
    Question(
        id="T4", dimension_id="technology", is_core=True,
        text_en="How does your organization handle model evaluation and testing?",
        text_zh="贵组织如何处理模型评估和测试？",
        options=_make_options([
            ("No formal evaluation process", "没有正式评估流程"),
            ("Manual testing before deployment", "部署前手动测试"),
            ("Standardized evaluation benchmarks and test suites", "标准化评估基准和测试套件"),
            ("Automated evaluation pipeline with bias/fairness checks", "自动化评估管道，有偏见/公平性检查"),
            ("Continuous evaluation with LLM-as-judge and human-in-the-loop", "持续评估，LLM-as-judge 和 human-in-the-loop"),
        ]),
    ),
    Question(
        id="T5", dimension_id="technology", is_core=False,
        text_en="How does your organization manage the AI technology stack?",
        text_zh="贵组织如何管理 AI 技术栈？",
        options=_make_options([
            ("No standardization; teams choose their own tools", "没有标准化；团队自选工具"),
            ("Recommended tools list but not enforced", "推荐工具清单但未强制"),
            ("Standardized tech stack with approved frameworks", "标准化技术栈，有批准的框架"),
            ("Centrally managed platform with vetted components", "集中管理的平台，有审查过的组件"),
            ("Platform engineering team maintaining AI golden paths", "平台工程团队维护 AI 黄金路径"),
        ]),
    ),
    Question(
        id="T6", dimension_id="technology", is_core=False,
        text_en="What is your approach to AI security (prompt injection, data leakage, adversarial attacks)?",
        text_zh="贵组织对 AI 安全（提示注入、数据泄漏、对抗攻击）的做法是什么？",
        options=_make_options([
            ("No AI-specific security measures", "没有 AI 专用安全措施"),
            ("Awareness of AI security risks but no formal program", "了解 AI 安全风险但没有正式计划"),
            ("Basic guardrails (input validation, output filtering)", "基本防护（输入验证、输出过滤）"),
            ("Comprehensive AI security program with red-teaming", "全面 AI 安全计划，有红队测试"),
            ("Proactive AI security with automated threat detection", "主动 AI 安全，自动威胁检测"),
        ]),
    ),

    # =========================================================================
    # TALENT & ORGANIZATION (人才与组织) — 5 questions (3 core + 2 deep)
    # =========================================================================
    Question(
        id="P1", dimension_id="talent", is_core=True,
        text_en="What does your AI team structure look like?",
        text_zh="贵组织的 AI 团队结构是怎样的？",
        options=_make_options([
            ("No dedicated AI roles", "没有专门的 AI 角色"),
            ("A few data scientists/ML engineers hired", "聘请了少量数据科学家/ML 工程师"),
            ("Dedicated AI/ML team with defined roles", "有专门的 AI/ML 团队并定义了角色"),
            ("AI CoE with embedded AI champions across business units", "AI 卓越中心，各业务单元有 AI 推广者"),
            ("AI capabilities distributed across all teams; AI is everyone's job", "AI 能力分布在所有团队；AI 是每个人的工作"),
        ]),
    ),
    Question(
        id="P2", dimension_id="talent", is_core=True,
        text_en="How mature are your AI training and upskilling programs?",
        text_zh="贵组织的 AI 培训和技能提升计划成熟度如何？",
        options=_make_options([
            ("No AI training programs", "没有 AI 培训计划"),
            ("Ad-hoc learning (individuals take online courses)", "临时学习（个人自行参加在线课程）"),
            ("Structured AI literacy and technical training programs", "结构化的 AI 素养和技术培训计划"),
            ("Role-based AI training with certification paths", "基于角色的 AI 培训，有认证路径"),
            ("Continuous learning culture with AI skills refreshed quarterly", "持续学习文化，AI 技能每季度更新"),
        ]),
    ),
    Question(
        id="P3", dimension_id="talent", is_core=True,
        text_en="How receptive is your organization to AI-driven change?",
        text_zh="贵组织对 AI 驱动的变革接受程度如何？",
        options=_make_options([
            ("Significant resistance; fear of job displacement", "显著抵触；担心工作被取代"),
            ("Mixed reactions; some enthusiasm, some concern", "反应不一；有些热情，有些担忧"),
            ("Generally positive with structured change management", "总体积极，有结构化变革管理"),
            ("Strong adoption culture with internal AI advocates", "强大的采纳文化，有内部 AI 倡导者"),
            ("AI-first mindset embedded in organizational culture", "AI 优先思维已融入组织文化"),
        ]),
    ),
    Question(
        id="P4", dimension_id="talent", is_core=False,
        text_en="How does your organization attract and retain AI talent?",
        text_zh="贵组织如何吸引和留住 AI 人才？",
        options=_make_options([
            ("Difficulty attracting AI talent; no employer brand for AI", "难以吸引 AI 人才；没有 AI 雇主品牌"),
            ("Competitive compensation but limited AI career paths", "有竞争力的薪酬但 AI 职业路径有限"),
            ("Defined AI career ladders with growth opportunities", "定义了 AI 职业阶梯和成长机会"),
            ("Strong AI employer brand with university partnerships", "强大的 AI 雇主品牌，与高校合作"),
            ("Industry-leading AI talent brand; thought leadership", "行业领先的 AI 人才品牌；思想领导力"),
        ]),
    ),
    Question(
        id="P5", dimension_id="talent", is_core=False,
        text_en="How well do business and technical teams collaborate on AI initiatives?",
        text_zh="业务团队和技术团队在 AI 项目上的协作程度如何？",
        options=_make_options([
            ("Minimal interaction; teams work in silos", "极少互动；团队各自为政"),
            ("Ad-hoc collaboration on specific projects", "在特定项目上临时协作"),
            ("Regular cross-functional meetings and shared goals", "定期跨职能会议和共同目标"),
            ("Embedded product teams with business and AI members", "嵌入式产品团队，有业务和 AI 成员"),
            ("Seamless collaboration; business teams self-serve AI tools", "无缝协作；业务团队自助使用 AI 工具"),
        ]),
    ),

    # =========================================================================
    # GOVERNANCE & ETHICS (治理与伦理) — 5 questions (3 core + 2 deep)
    # =========================================================================
    Question(
        id="G1", dimension_id="governance", is_core=True,
        text_en="Does your organization have an AI governance framework?",
        text_zh="贵组织是否有 AI 治理框架？",
        options=_make_options([
            ("No AI governance", "没有 AI 治理"),
            ("Informal guidelines for AI use", "AI 使用的非正式指南"),
            ("Formal AI governance framework with policies", "正式 AI 治理框架，有政策"),
            ("Active AI governance committee with enforcement", "活跃的 AI 治理委员会，有执行力"),
            ("Industry-leading governance integrated into all AI workflows", "行业领先的治理，集成到所有 AI 工作流"),
        ]),
    ),
    Question(
        id="G2", dimension_id="governance", is_core=True,
        text_en="How does your organization address responsible AI (bias, fairness, transparency)?",
        text_zh="贵组织如何处理负责任 AI（偏见、公平性、透明度）？",
        options=_make_options([
            ("Not addressed", "未处理"),
            ("Awareness but no formal processes", "有意识但没有正式流程"),
            ("Bias testing and documentation for production models", "生产模型的偏见测试和文档记录"),
            ("Automated bias detection, fairness metrics, model cards", "自动偏见检测、公平性指标、模型卡片"),
            ("Proactive responsible AI with external audits and public reporting", "主动负责任 AI，外部审计和公开报告"),
        ]),
    ),
    Question(
        id="G3", dimension_id="governance", is_core=True,
        text_en="What is your organization's readiness for AI regulations (EU AI Act, NIST AI RMF)?",
        text_zh="贵组织对 AI 法规（EU AI Act, NIST AI RMF）的准备程度如何？",
        options=_make_options([
            ("Unaware of regulatory requirements", "不了解监管要求"),
            ("Aware but no action taken", "了解但未采取行动"),
            ("Gap analysis completed; compliance roadmap in progress", "差距分析已完成；合规路线图制定中"),
            ("Compliance program in place for applicable regulations", "已建立适用法规的合规计划"),
            ("Fully compliant with proactive regulatory engagement", "完全合规，并主动参与监管对话"),
        ]),
    ),
    Question(
        id="G4", dimension_id="governance", is_core=False,
        text_en="How does your organization manage AI risk?",
        text_zh="贵组织如何管理 AI 风险？",
        options=_make_options([
            ("AI risks not formally assessed", "AI 风险未正式评估"),
            ("Ad-hoc risk assessment for individual projects", "对个别项目进行临时风险评估"),
            ("AI risk register with regular reviews", "AI 风险登记册，定期审查"),
            ("Automated risk monitoring with escalation procedures", "自动风险监控，有升级流程"),
            ("Enterprise AI risk management integrated with ERM framework", "企业 AI 风险管理与 ERM 框架集成"),
        ]),
    ),
    Question(
        id="G5", dimension_id="governance", is_core=False,
        text_en="Does your organization maintain audit trails for AI decisions?",
        text_zh="贵组织是否维护 AI 决策的审计追踪？",
        options=_make_options([
            ("No audit trails", "没有审计追踪"),
            ("Basic logging for some AI systems", "部分 AI 系统有基本日志"),
            ("Structured audit logs for production AI systems", "生产 AI 系统有结构化审计日志"),
            ("Comprehensive audit trails with explainability records", "全面审计追踪，有可解释性记录"),
            ("Real-time audit trails with automated compliance reporting", "实时审计追踪，自动合规报告"),
        ]),
    ),

    # =========================================================================
    # OPERATIONS & SCALE (运营与规模化) — 5 questions (3 core + 2 deep)
    # =========================================================================
    Question(
        id="O1", dimension_id="operations", is_core=True,
        text_en="How many AI/ML models does your organization have in production?",
        text_zh="贵组织有多少 AI/ML 模型在生产中运行？",
        options=_make_options([
            ("None", "没有"),
            ("1-3 models", "1-3 个模型"),
            ("4-15 models with defined SLAs", "4-15 个模型，有定义的 SLA"),
            ("16-50+ models managed as a portfolio", "16-50+ 个模型，作为组合管理"),
            ("100+ models with autonomous lifecycle management", "100+ 个模型，自主生命周期管理"),
        ]),
    ),
    Question(
        id="O2", dimension_id="operations", is_core=True,
        text_en="What is your MLOps maturity level?",
        text_zh="贵组织的 MLOps 成熟度如何？",
        options=_make_options([
            ("No MLOps practices", "没有 MLOps 实践"),
            ("Manual model deployment and monitoring", "手动模型部署和监控"),
            ("Semi-automated CI/CD for ML with basic monitoring", "半自动化的 ML CI/CD，有基本监控"),
            ("Fully automated MLOps pipeline with drift detection", "全自动 MLOps 管道，有漂移检测"),
            ("Self-optimizing MLOps with automated retraining and canary releases", "自优化 MLOps，自动再训练和金丝雀发布"),
        ]),
    ),
    Question(
        id="O3", dimension_id="operations", is_core=True,
        text_en="How does your organization monitor AI model performance in production?",
        text_zh="贵组织如何监控生产中 AI 模型的性能？",
        options=_make_options([
            ("No monitoring", "没有监控"),
            ("Basic uptime monitoring only", "仅基本可用性监控"),
            ("Model-specific performance metrics with alerting", "模型特定性能指标和告警"),
            ("Comprehensive monitoring: drift, bias, latency, cost", "全面监控：漂移、偏见、延迟、成本"),
            ("Real-time observability with automated remediation", "实时可观测性，自动修复"),
        ]),
    ),
    Question(
        id="O4", dimension_id="operations", is_core=False,
        text_en="How does your organization handle model retraining?",
        text_zh="贵组织如何处理模型再训练？",
        options=_make_options([
            ("No retraining process", "没有再训练流程"),
            ("Manual retraining when performance drops", "性能下降时手动再训练"),
            ("Scheduled retraining with performance validation", "定期再训练，有性能验证"),
            ("Trigger-based automated retraining pipeline", "基于触发器的自动再训练管道"),
            ("Continuous learning with automated A/B testing and rollback", "持续学习，自动 A/B 测试和回退"),
        ]),
    ),
    Question(
        id="O5", dimension_id="operations", is_core=False,
        text_en="How does your organization manage AI-related costs?",
        text_zh="贵组织如何管理 AI 相关成本？",
        options=_make_options([
            ("No cost tracking for AI", "没有 AI 成本追踪"),
            ("Basic cloud billing review", "基本的云计费审查"),
            ("Cost allocation by project/model with budgets", "按项目/模型分配成本并有预算"),
            ("Automated cost optimization (spot instances, model compression)", "自动成本优化（竞价实例、模型压缩）"),
            ("FinOps for AI with real-time cost-per-inference tracking", "AI 的 FinOps，实时推理成本追踪"),
        ]),
    ),
]


def get_questions(dimension_id: str | None = None, core_only: bool = False) -> list[Question]:
    qs = QUESTIONS
    if dimension_id:
        qs = [q for q in qs if q.dimension_id == dimension_id]
    if core_only:
        qs = [q for q in qs if q.is_core]
    return qs
