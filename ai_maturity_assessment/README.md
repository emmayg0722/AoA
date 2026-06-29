# AI Maturity Assessment Agent
# AI 成熟度评估工具

A structured, interactive assessment tool for evaluating enterprise AI maturity across 6 key dimensions, based on frameworks from Gartner, McKinsey, Deloitte, and Accenture.

咨询公司 AI Architect 使用的企业 AI 成熟度评估工具，覆盖 6 大维度，参考 Gartner、McKinsey、Deloitte、Accenture 等头部咨询公司的评估框架。

## Features / 功能特点

- **Two assessment modes / 两种评估模式**: Core (~20 questions, 10 min) and Comprehensive (~33 questions, 20 min)
- **6 dimensions / 6 大评估维度**: Strategy, Data, Technology, Talent, Governance, Operations
- **5-level maturity model / 5 级成熟度模型**: Exploring → Experimenting → Operationalizing → Scaling → Transforming
- **Bilingual / 中英双语**: All questions, options, and reports in English and Chinese
- **Auto-generated reports / 自动生成报告**: Markdown reports with scores, gap analysis, and roadmap
- **Batch mode / 批量模式**: Process pre-collected answers from JSON files

## Quick Start / 快速开始

```bash
cd ai_maturity_assessment

# Run interactive assessment / 运行交互式评估
python main.py

# Generate demo report / 生成示例报告
python main.py demo

# Export questions as JSON / 导出问题为 JSON
python main.py questions --format json

# Batch assessment from file / 从文件批量评估
python main.py batch answers.json --company "Acme Corp" --industry "Finance"
```

## Assessment Dimensions / 评估维度

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Strategy & Vision (战略与愿景) | 20% | Executive sponsorship, AI strategy, investment |
| Data & Infrastructure (数据与基础设施) | 20% | Data quality, governance, cloud readiness |
| Technology & Architecture (技术与架构) | 18% | AI/ML platforms, GenAI, integration |
| Talent & Organization (人才与组织) | 15% | Team structure, training, culture |
| Governance & Ethics (治理与伦理) | 15% | Policies, responsible AI, compliance |
| Operations & Scale (运营与规模化) | 12% | MLOps, monitoring, production models |

## Maturity Levels / 成熟度等级

| Level | Name | Description |
|-------|------|-------------|
| 1 | Exploring (探索期) | Ad-hoc, no formal strategy |
| 2 | Experimenting (实验期) | Isolated pilots, limited governance |
| 3 | Operationalizing (运营化) | Production AI, emerging governance |
| 4 | Scaling (规模化) | Enterprise-wide, mature governance |
| 5 | Transforming (转型期) | AI-first culture, continuous innovation |

## Output / 输出

The tool generates:
- **Markdown report** (`output/assessment_*.md`) with executive summary, per-dimension analysis, gap analysis, and roadmap
- **JSON data** (`output/assessment_*.json`) with raw scores for further analysis

## Project Structure / 项目结构

```
ai_maturity_assessment/
├── main.py                    # Entry point / 入口
├── README.md                  # This file
└── assessment/
    ├── __init__.py
    ├── model.py               # Maturity model definitions / 成熟度模型定义
    ├── questions.py            # Question bank (33 questions) / 题库
    ├── scoring.py              # Scoring engine / 评分引擎
    ├── engine.py               # Interactive CLI engine / 交互引擎
    └── report.py               # Report generator / 报告生成器
```

## For Consultants / 咨询顾问使用指南

1. **Client meeting prep**: Run `python main.py questions --format json` to export questions for survey tools
2. **On-site assessment**: Use `python main.py` for live interactive assessment with stakeholders
3. **Post-assessment**: Reports auto-generate with scores, gaps, and actionable recommendations
4. **Tracking progress**: Re-run assessments quarterly to measure improvement
