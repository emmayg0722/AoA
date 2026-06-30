"""AI Maturity Assessment — Streamlit Web App."""

import json
import datetime
from pathlib import Path

import streamlit as st

from assessment.model import DIMENSIONS, LEVEL_DESCRIPTIONS, MaturityLevel
from assessment.questions import get_questions
from assessment.scoring import compute_scores, get_gap_analysis, get_level_label
from assessment.report import generate_report


# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Maturity Assessment",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .score-card h1 {
        color: white !important;
        font-size: 3rem !important;
        margin: 0 !important;
    }
    .score-card p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    .dim-card {
        background: #f8f9fa;
        padding: 1.2rem;
        border-radius: 0.8rem;
        border-left: 4px solid #667eea;
        margin-bottom: 0.8rem;
    }
    .gap-high { color: #e74c3c; font-weight: bold; }
    .gap-medium { color: #f39c12; font-weight: bold; }
    .gap-low { color: #27ae60; font-weight: bold; }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
</style>
""", unsafe_allow_html=True)


# ── Session state init ───────────────────────────────────────────────────────

if "page" not in st.session_state:
    st.session_state.page = "setup"
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "current_dim_idx" not in st.session_state:
    st.session_state.current_dim_idx = 0


# ── Helper functions ─────────────────────────────────────────────────────────

LEVEL_COLORS = {1: "#e74c3c", 2: "#e67e22", 3: "#f1c40f", 4: "#2ecc71", 5: "#3498db"}


def level_badge(level: MaturityLevel) -> str:
    desc = LEVEL_DESCRIPTIONS[level]
    color = LEVEL_COLORS[level.value]
    return f'<span style="background:{color}; color:white; padding:2px 10px; border-radius:12px; font-size:0.85rem;">L{level.value} {desc["en"]} ({desc["zh"]})</span>'


def score_bar(score: float, max_val: float = 5.0) -> None:
    st.progress(score / max_val)


# ── PAGE: Setup ──────────────────────────────────────────────────────────────

def page_setup():
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("🧠 AI Maturity Assessment")
    st.markdown("**AI 成熟度评估工具**")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Assessment Info / 评估信息")
        st.session_state.company = st.text_input(
            "Company Name / 企业名称", value="", placeholder="e.g. Acme Corp"
        )
        st.session_state.industry = st.selectbox(
            "Industry / 行业",
            ["Technology", "Financial Services", "Healthcare", "Manufacturing",
             "Retail", "Energy", "Telecommunications", "Government", "Education", "Other"],
        )
        st.session_state.assessor = st.text_input(
            "Assessor / 评估师", value="", placeholder="e.g. AI Architect"
        )

    with col2:
        st.subheader("Settings / 设置")
        mode = st.radio(
            "Assessment Mode / 评估模式",
            ["Core (~21 questions, 10 min) / 核心评估", "Comprehensive (~33 questions, 20 min) / 全面评估"],
            index=0,
        )
        st.session_state.core_only = mode.startswith("Core")

        target = st.select_slider(
            "Target Maturity Level / 目标成熟度",
            options=[3, 4, 5],
            value=4,
            format_func=lambda x: f"Level {x} — {LEVEL_DESCRIPTIONS[MaturityLevel(x)]['en']} ({LEVEL_DESCRIPTIONS[MaturityLevel(x)]['zh']})",
        )
        st.session_state.target_level = target

    st.markdown("---")

    st.subheader("Assessment Dimensions / 评估维度")
    cols = st.columns(3)
    for i, dim in enumerate(DIMENSIONS):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="dim-card">
                <strong>{dim.name_en}</strong><br/>
                <em>{dim.name_zh}</em> — Weight: {dim.weight:.0%}<br/>
                <small>{dim.description}</small>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("▶️ Start Assessment / 开始评估", type="primary", use_container_width=True):
        st.session_state.answers = {}
        st.session_state.current_dim_idx = 0
        st.session_state.page = "assess"
        st.rerun()


# ── PAGE: Assessment ─────────────────────────────────────────────────────────

def page_assess():
    core_only = st.session_state.get("core_only", True)
    questions = get_questions(core_only=core_only)
    total = len(questions)

    # Group questions by dimension
    dim_groups: list[tuple[str, list]] = []
    current_dim = None
    for q in questions:
        if q.dimension_id != current_dim:
            current_dim = q.dimension_id
            dim_obj = next(d for d in DIMENSIONS if d.id == current_dim)
            dim_groups.append((dim_obj, []))
        dim_groups[-1][1].append(q)

    dim_idx = st.session_state.current_dim_idx
    if dim_idx >= len(dim_groups):
        st.session_state.page = "results"
        st.rerun()
        return

    dim, dim_questions = dim_groups[dim_idx]

    # Progress
    answered = len(st.session_state.answers)
    st.progress(answered / total, text=f"Progress: {answered}/{total} questions")

    # Dimension header
    st.markdown(f"### 📊 {dim.name_en} / {dim.name_zh}")
    st.caption(dim.description)
    st.markdown("---")

    # Questions in this dimension
    all_answered = True
    for q in dim_questions:
        st.markdown(f"**{q.text_en}**")
        st.markdown(f"*{q.text_zh}*")

        option_labels = [f"{opt['value']}. {opt['text_en']} / {opt['text_zh']}" for opt in q.options]

        prev_answer = st.session_state.answers.get(q.id)
        prev_index = (prev_answer - 1) if prev_answer else None

        selected = st.radio(
            f"Select / 请选择 ({q.id})",
            options=range(len(option_labels)),
            format_func=lambda i, labels=option_labels: labels[i],
            index=prev_index,
            key=f"q_{q.id}",
            label_visibility="collapsed",
        )

        if selected is not None:
            st.session_state.answers[q.id] = selected + 1
        else:
            all_answered = False

        st.markdown("---")

    # Navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if dim_idx > 0:
            if st.button("⬅️ Previous / 上一步"):
                st.session_state.current_dim_idx -= 1
                st.rerun()
    with col2:
        st.markdown(f"<center>Section {dim_idx + 1} of {len(dim_groups)}</center>", unsafe_allow_html=True)
    with col3:
        if dim_idx < len(dim_groups) - 1:
            if st.button("Next ➡️ / 下一步", type="primary"):
                st.session_state.current_dim_idx += 1
                st.rerun()
        else:
            if st.button("📊 View Results / 查看结果", type="primary"):
                st.session_state.page = "results"
                st.rerun()


# ── PAGE: Results ────────────────────────────────────────────────────────────

def page_results():
    answers = st.session_state.answers
    if not answers:
        st.warning("No answers recorded. Please complete the assessment first.")
        if st.button("↩️ Back to Setup"):
            st.session_state.page = "setup"
            st.rerun()
        return

    mode = "core" if st.session_state.get("core_only", True) else "comprehensive"
    target = st.session_state.get("target_level", 4)
    company = st.session_state.get("company", "Assessment Target") or "Assessment Target"
    industry = st.session_state.get("industry", "General")
    assessor = st.session_state.get("assessor", "AI Architect") or "AI Architect"

    result = compute_scores(answers, assessment_mode=mode)
    level_info = LEVEL_DESCRIPTIONS[result.overall_level]

    # ── Executive Summary ──
    st.markdown(f"""
    <div class="score-card">
        <h1>{result.overall_score:.1f} / 5.0</h1>
        <p>L{result.overall_level.value} — {level_info['en']} ({level_info['zh']})</p>
        <p style="font-size:0.9rem; margin-top:0.5rem;">{level_info['description']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"**Company / 企业:** {company} &nbsp;|&nbsp; **Industry / 行业:** {industry} &nbsp;|&nbsp; **Assessor / 评估师:** {assessor}")
    st.markdown("---")

    # ── Dimension Scores (radar-like bar chart) ──
    st.subheader("📊 Dimension Scores / 维度评分")

    cols = st.columns(2)
    for i, ds in enumerate(result.dimension_scores):
        with cols[i % 2]:
            dl = LEVEL_DESCRIPTIONS[ds.level]
            st.markdown(f"**{ds.dimension_name_en}** ({ds.dimension_name_zh})")
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.progress(ds.raw_score / 5.0)
            with col_b:
                st.markdown(f"**{ds.raw_score:.1f}** / 5.0")
            st.markdown(level_badge(ds.level), unsafe_allow_html=True)
            st.markdown("")

    st.markdown("---")

    # ── Radar Chart ──
    st.subheader("🕸️ Maturity Radar / 成熟度雷达图")

    import math

    chart_data = {
        "Dimension": [ds.dimension_name_en for ds in result.dimension_scores],
        "Score": [ds.raw_score for ds in result.dimension_scores],
        "Target": [target] * len(result.dimension_scores),
    }

    # Use Streamlit's built-in bar chart as a simple visualization
    import pandas as pd
    df = pd.DataFrame({
        "Dimension": [f"{ds.dimension_name_en}\n({ds.dimension_name_zh})" for ds in result.dimension_scores],
        "Current Score": [ds.raw_score for ds in result.dimension_scores],
        "Target Level": [float(target)] * len(result.dimension_scores),
    })
    df = df.set_index("Dimension")
    st.bar_chart(df, color=["#667eea", "#e0e0e0"])

    st.markdown("---")

    # ── Gap Analysis ──
    st.subheader("🔍 Gap Analysis / 差距分析")

    gaps = get_gap_analysis(result, target)
    if gaps:
        gap_df = pd.DataFrame(gaps)
        gap_df = gap_df[["dimension_name", "current_score", "target_score", "gap", "priority"]]
        gap_df.columns = ["Dimension / 维度", "Current / 当前", "Target / 目标", "Gap / 差距", "Priority / 优先级"]

        def highlight_priority(val):
            colors = {"High": "background-color: #fadbd8", "Medium": "background-color: #fdebd0", "Low": "background-color: #d5f5e3"}
            return colors.get(val, "")

        styled = gap_df.style.map(highlight_priority, subset=["Priority / 优先级"])
        st.dataframe(styled, use_container_width=True, hide_index=True)
    else:
        st.success("🎉 No gaps! All dimensions meet or exceed the target level.")

    st.markdown("---")

    # ── Recommendations ──
    st.subheader("💡 Key Recommendations / 关键建议")

    from assessment.report import _recommendations_for_dimension

    high_gaps = [g for g in gaps if g["priority"] == "High"]
    med_gaps = [g for g in gaps if g["priority"] == "Medium"]

    if high_gaps:
        st.markdown("#### 🔴 High Priority / 高优先级 (Months 1-3)")
        for g in high_gaps:
            ds_match = next((ds for ds in result.dimension_scores if ds.dimension_id == g["dimension_id"]), None)
            if ds_match:
                recs = _recommendations_for_dimension(ds_match)
                with st.expander(f"**{g['dimension_name']}** — Gap: {g['gap']:.1f}"):
                    for r in recs:
                        st.markdown(f"- {r}")

    if med_gaps:
        st.markdown("#### 🟡 Medium Priority / 中优先级 (Months 4-9)")
        for g in med_gaps:
            ds_match = next((ds for ds in result.dimension_scores if ds.dimension_id == g["dimension_id"]), None)
            if ds_match:
                recs = _recommendations_for_dimension(ds_match)
                with st.expander(f"**{g['dimension_name']}** — Gap: {g['gap']:.1f}"):
                    for r in recs:
                        st.markdown(f"- {r}")

    low_gaps = [g for g in gaps if g["priority"] == "Low"]
    if low_gaps:
        st.markdown("#### 🟢 Low Priority / 低优先级 (Months 10-18)")
        for g in low_gaps:
            ds_match = next((ds for ds in result.dimension_scores if ds.dimension_id == g["dimension_id"]), None)
            if ds_match:
                recs = _recommendations_for_dimension(ds_match)
                with st.expander(f"**{g['dimension_name']}** — Gap: {g['gap']:.1f}"):
                    for r in recs:
                        st.markdown(f"- {r}")

    st.markdown("---")

    # ── Download Buttons ──
    st.subheader("📥 Download Report / 下载报告")

    report_md = generate_report(
        result,
        company_name=company,
        industry=industry,
        assessor=assessor,
        target_level=target,
    )

    data_json = json.dumps({
        "metadata": {
            "company": company,
            "industry": industry,
            "assessor": assessor,
            "mode": mode,
            "target_level": target,
            "date": datetime.datetime.now().isoformat(),
        },
        "answers": answers,
        "scores": {
            "overall_score": result.overall_score,
            "overall_level": result.overall_level.value,
            "dimensions": [
                {
                    "id": ds.dimension_id,
                    "name_en": ds.dimension_name_en,
                    "name_zh": ds.dimension_name_zh,
                    "score": ds.raw_score,
                    "level": ds.level.value,
                    "weight": ds.weight,
                }
                for ds in result.dimension_scores
            ],
        },
    }, indent=2, ensure_ascii=False)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "📄 Download Markdown Report",
            data=report_md,
            file_name=f"AI_Maturity_Assessment_{company.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            "📊 Download JSON Data",
            data=data_json,
            file_name=f"AI_Maturity_Data_{company.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True,
        )
    with col3:
        if st.button("🔄 New Assessment / 重新评估", use_container_width=True):
            st.session_state.page = "setup"
            st.session_state.answers = {}
            st.session_state.current_dim_idx = 0
            st.rerun()


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🧠 AI Maturity Assessment")
    st.markdown("---")

    page_labels = {
        "setup": "1️⃣ Setup",
        "assess": "2️⃣ Assessment",
        "results": "3️⃣ Results",
    }
    current = st.session_state.page
    for key, label in page_labels.items():
        if key == current:
            st.markdown(f"**→ {label}**")
        else:
            st.markdown(f"&nbsp;&nbsp;&nbsp;{label}")

    st.markdown("---")

    if current == "assess":
        answered = len(st.session_state.answers)
        total = len(get_questions(core_only=st.session_state.get("core_only", True)))
        st.metric("Progress", f"{answered}/{total}")

    st.markdown("---")
    st.caption("Built for AI Architects at consulting firms.")
    st.caption("为咨询公司 AI 架构师打造。")


# ── Router ───────────────────────────────────────────────────────────────────

page = st.session_state.page
if page == "setup":
    page_setup()
elif page == "assess":
    page_assess()
elif page == "results":
    page_results()
