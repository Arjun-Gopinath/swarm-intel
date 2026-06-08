"""Streamlit UI for swarm-intel — Multi-Agent Due Diligence Swarm."""

import os
import io
import re
import time
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from graph.workflow import swarm

st.set_page_config(
    page_title="swarm-intel",
    page_icon="🕵️",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #0e1117; }

.stMarkdown p, .stMarkdown li { font-size: 1rem; line-height: 1.8; }
.stMarkdown h1 { font-size: 1.75rem; }
.stMarkdown h2 { font-size: 1.4rem; }
.stMarkdown h3 { font-size: 1.15rem; }
.stCaption p   { font-size: 0.9rem; color: #8b949e; }
.stAlert p     { font-size: 0.95rem; }

.hero-title {
    text-align: center;
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -1px;
    color: #ffffff;
    margin-bottom: 0.25rem;
}
.hero-subtitle {
    text-align: center;
    color: #8b949e;
    font-size: 1rem;
    margin-bottom: 2rem;
}

.badge-row {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin: 0.75rem 0 1.5rem;
}
.badge {
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid;
}
.badge-llm    { background: #1a2a3a; color: #58a6ff; border-color: #1f6feb; }
.badge-search { background: #1a2a1a; color: #56d364; border-color: #2ea043; }

.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #8b949e;
    margin-bottom: 0.75rem;
}

/* Pipeline status cards */
.pipeline-card {
    border-radius: 8px;
    padding: 0.6rem 0.85rem;
    border: 1px solid;
    display: flex;
    align-items: center;
    gap: 0.45rem;
    margin-bottom: 0;
}
.pipeline-card.waiting  { border-color: #30363d; background: #161b22; }
.pipeline-card.running  { border-color: #1f6feb; background: #0d1f33; }
.pipeline-card.complete { border-color: #2ea043; background: #0d1f0d; }
.pipeline-card.error    { border-color: #da3633; background: #1f0d0d; }

.pc-icon { font-size: 1.05rem; line-height: 1; }
.pc-name { font-weight: 600; font-size: 0.82rem; color: #e6edf3; flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.status-pill {
    padding: 0.08rem 0.45rem;
    border-radius: 999px;
    font-size: 0.62rem;
    font-weight: 700;
    white-space: nowrap;
    flex-shrink: 0;
}
.pill-waiting  { background: #21262d; color: #8b949e; }
.pill-running  { background: #1f3a5f; color: #58a6ff; }
.pill-complete { background: #1a3a1a; color: #56d364; }
.pill-error    { background: #3a1a1a; color: #f85149; }

/* Pipeline flow layout */
.pipeline-row {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    margin-bottom: 0;
}
.connector-down {
    text-align: center;
    color: #30363d;
    font-size: 1rem;
    margin: 0.3rem 0;
    letter-spacing: 6px;
}
.connector-right {
    color: #30363d;
    font-size: 1rem;
    flex-shrink: 0;
    padding: 0 0.2rem;
}
.downstream-wrap {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    align-items: center;
}
.downstream-card {
    width: 36%;
}

/* Output tab content area */
.tab-waiting {
    color: #8b949e;
    font-size: 0.88rem;
    padding: 0.5rem 0;
    font-style: italic;
}

.context-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin: 1.5rem 0 2rem;
}
.context-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
}
.context-card.green { border-left: 3px solid #2ea043; }
.context-card.amber { border-left: 3px solid #d29922; }
.context-card h4 {
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin: 0 0 0.75rem;
}
.context-card.green h4 { color: #56d364; }
.context-card.amber h4 { color: #e3b341; }
.context-card ul {
    margin: 0;
    padding-left: 1.1rem;
    color: #8b949e;
    font-size: 0.82rem;
    line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for _k, _v in [("running", False), ("results", None), ("last_query", "")]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown('<h2 class="hero-title">🕵️ swarm-intel</h2>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-subtitle">Multi-agent due diligence research swarm</p>',
    unsafe_allow_html=True,
)

llm_provider    = os.environ.get("LLM_PROVIDER", "ollama")
llm_model       = os.environ.get("LLM_MODEL", "")
search_provider = os.environ.get("SEARCH_PROVIDER", "duckduckgo")
llm_label       = f"{llm_provider}/{llm_model}" if llm_model else llm_provider

st.markdown(f"""
<div class="badge-row">
  <span class="badge badge-llm">🤖 {llm_label}</span>
  <span class="badge badge-search">🔍 {search_provider}</span>
</div>
""", unsafe_allow_html=True)

_, ctx_col, _ = st.columns([1, 3, 1])
with ctx_col:
    st.markdown("""
<div class="context-grid">
  <div class="context-card green">
    <h4>✅ Good for</h4>
    <ul>
      <li>Early-stage investment screening</li>
      <li>Competitive landscape research</li>
      <li>Vendor or partner due diligence</li>
      <li>Quick background check on a company</li>
      <li>Identifying red flags before a meeting</li>
    </ul>
  </div>
  <div class="context-card amber">
    <h4>⚠️ Not a replacement for</h4>
    <ul>
      <li>Professional legal or financial advice</li>
      <li>Verified financial audits or filings</li>
      <li>Real-time stock or market data</li>
      <li>Deep technical code audits</li>
      <li>Official regulatory compliance checks</li>
    </ul>
  </div>
</div>
""", unsafe_allow_html=True)

_, center_col, _ = st.columns([1, 3, 1])
with center_col:
    query = st.text_input(
        "Company or topic",
        placeholder="e.g. Stripe, OpenAI, Thoughtworks",
        label_visibility="collapsed",
        disabled=st.session_state.running,
    )
    run = st.button(
        "⬛ Running swarm..." if st.session_state.running else "🚀 Run Swarm",
        type="primary",
        disabled=not bool(query) or st.session_state.running,
        use_container_width=True,
    )

# ── Agent metadata ────────────────────────────────────────────────────────────
AGENTS = [
    {"key": "news_agent",       "icon": "📰", "name": "News",       "result_key": "news_results",       "wait": "Searching recent news, funding & leadership changes…"},
    {"key": "financial_agent",  "icon": "💰", "name": "Financial",  "result_key": "financial_results",  "wait": "Fetching revenue, valuation & funding history…"},
    {"key": "linkedin_agent",   "icon": "👥", "name": "LinkedIn",   "result_key": "linkedin_results",   "wait": "Looking up headcount, leadership & team growth…"},
    {"key": "github_agent",     "icon": "💻", "name": "GitHub",     "result_key": "github_results",     "wait": "Analysing OSS activity & tech stack signals…"},
    {"key": "regulatory_agent", "icon": "⚖️", "name": "Regulatory", "result_key": "regulatory_results", "wait": "Scanning for lawsuits, compliance risks & violations…"},
]
DOWNSTREAM = [
    {"key": "validator",   "icon": "✅", "name": "Validator",   "result_key": "validated_findings", "wait": "Cross-checking findings and flagging conflicts…"},
    {"key": "synthesizer", "icon": "📋", "name": "Synthesizer", "result_key": "final_report",       "wait": "Writing the final due diligence report…"},
]
ALL_AGENTS = {a["key"]: a for a in AGENTS + DOWNSTREAM}


def _card_html(icon: str, name: str, status: str) -> str:
    pill_cls = {
        "waiting":  "pill-waiting",
        "running":  "pill-running",
        "complete": "pill-complete",
        "error":    "pill-error",
    }[status]
    pill_label = {
        "waiting":  "○ Queued",
        "running":  "● Running",
        "complete": "✓ Done",
        "error":    "✗ Error",
    }[status]
    return (
        f'<div class="pipeline-card {status}">'
        f'<span class="pc-icon">{icon}</span>'
        f'<span class="pc-name">{name}</span>'
        f'<span class="status-pill {pill_cls}">{pill_label}</span>'
        f'</div>'
    )


# ── Export helpers ────────────────────────────────────────────────────────────

def _report_to_pdf(markdown_text: str, company: str) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib import colors

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm,
    )

    styles = getSampleStyleSheet()
    style_h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=18, spaceAfter=6, textColor=colors.HexColor("#1a1a2e"))
    style_h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14, spaceAfter=4, textColor=colors.HexColor("#16213e"))
    style_h3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11, spaceAfter=3, textColor=colors.HexColor("#0f3460"))
    style_body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=16, spaceAfter=6)
    style_bullet = ParagraphStyle("Bullet", parent=style_body, leftIndent=12, bulletIndent=0, spaceAfter=3)

    story = []

    # Cover title
    story.append(Paragraph(f"Due Diligence Report: {company}", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 6))

    for line in markdown_text.splitlines():
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 4))
        elif stripped.startswith("### "):
            story.append(Paragraph(stripped[4:], style_h3))
        elif stripped.startswith("## "):
            story.append(Paragraph(stripped[3:], style_h2))
        elif stripped.startswith("# "):
            story.append(Paragraph(stripped[2:], style_h1))
        elif stripped.startswith(("- ", "* ", "• ")):
            text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", stripped[2:])
            story.append(Paragraph(f"• {text}", style_bullet))
        else:
            text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", stripped)
            story.append(Paragraph(text, style_body))

    doc.build(story)
    return buf.getvalue()


# ── Trigger run ───────────────────────────────────────────────────────────────
if run and query:
    st.session_state.running = True
    st.session_state.results = None
    st.session_state.last_query = query
    st.rerun()

if st.session_state.running or st.session_state.results:
    active_query = st.session_state.last_query
    is_running   = st.session_state.running
    res          = st.session_state.results or {}

    st.markdown("---")

    # ── Pipeline visualization ────────────────────────────────────────────────
    st.markdown('<p class="section-label">Agent Pipeline</p>', unsafe_allow_html=True)

    # Research agents — full width, 5 columns
    pipe_cols = st.columns(5, gap="small")
    pipe_phs  = {}
    for col, agent in zip(pipe_cols, AGENTS):
        with col:
            ph = st.empty()
            ph.markdown(
                _card_html(agent["icon"], agent["name"], "running" if is_running else "complete"),
                unsafe_allow_html=True,
            )
            pipe_phs[agent["key"]] = ph

    # Converging arrows
    st.markdown('<p class="connector-down">↓ · · · · ↓</p>', unsafe_allow_html=True)

    # Validator + Synthesizer — centered pair
    _, ds_col, _ = st.columns([0.75, 3.5, 0.75])
    with ds_col:
        val_c, arr_c, syn_c = st.columns([1, 0.08, 1], gap="small")
        with val_c:
            val_ph = st.empty()
            val_ph.markdown(
                _card_html("✅", "Validator", "waiting" if is_running else "complete"),
                unsafe_allow_html=True,
            )
            pipe_phs["validator"] = val_ph
        with arr_c:
            st.markdown('<p class="connector-right" style="padding-top:0.55rem">→</p>', unsafe_allow_html=True)
        with syn_c:
            syn_ph = st.empty()
            syn_ph.markdown(
                _card_html("📋", "Synthesizer", "waiting" if is_running else "complete"),
                unsafe_allow_html=True,
            )
            pipe_phs["synthesizer"] = syn_ph

    # ── Output tabs ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<p class="section-label">Agent Outputs</p>', unsafe_allow_html=True)

    tab_labels = ["📰 News", "💰 Financial", "👥 LinkedIn", "💻 GitHub", "⚖️ Regulatory", "✅ Validator"]
    tabs = st.tabs(tab_labels)
    tab_phs: dict = {}

    for tab, agent in zip(tabs[:5], AGENTS):
        with tab:
            ph = st.empty()
            if not is_running:
                items = res.get(agent["result_key"], [])
                with ph.container():
                    if items:
                        st.markdown(items[0].get("content", "No output."))
                    else:
                        st.info("No results returned.")
            else:
                ph.markdown(f'<p class="tab-waiting">{agent["wait"]}</p>', unsafe_allow_html=True)
            tab_phs[agent["key"]] = ph

    with tabs[5]:
        val_tab_ph = st.empty()
        if not is_running:
            validated = res.get("validated_findings", {})
            with val_tab_ph.container():
                st.markdown(validated.get("summary", "No validation output."))
        else:
            val_tab_ph.markdown('<p class="tab-waiting">Waiting for research agents to complete…</p>', unsafe_allow_html=True)
        tab_phs["validator"] = val_tab_ph

    # ── Stream ────────────────────────────────────────────────────────────────
    if is_running:
        final_state: dict = {}
        start = time.time()
        research_done = 0

        for chunk in swarm.stream(
            {
                "query":               active_query,
                "news_results":        [],
                "financial_results":   [],
                "linkedin_results":    [],
                "github_results":      [],
                "regulatory_results":  [],
                "errors":              [],
            },
            stream_mode="updates",
        ):
            for node_name, node_output in chunk.items():
                if node_name not in ALL_AGENTS:
                    continue

                final_state.update(node_output)
                agent_info = ALL_AGENTS[node_name]
                result_key = agent_info["result_key"]
                errors     = node_output.get("errors", [])
                has_error  = bool(errors) and not node_output.get(result_key)
                status     = "error" if has_error else "complete"

                # Update pipeline card
                if node_name in pipe_phs:
                    pipe_phs[node_name].markdown(
                        _card_html(agent_info["icon"], agent_info["name"], status),
                        unsafe_allow_html=True,
                    )

                # When a research agent completes, flip downstream to "running"
                if node_name in {a["key"] for a in AGENTS}:
                    research_done += 1
                    if research_done == len(AGENTS):
                        pipe_phs["validator"].markdown(
                            _card_html("✅", "Validator", "running"), unsafe_allow_html=True
                        )
                elif node_name == "validator":
                    pipe_phs["synthesizer"].markdown(
                        _card_html("📋", "Synthesizer", "running"), unsafe_allow_html=True
                    )

                # Update tab output (not synthesizer — its output goes to report)
                if node_name in tab_phs:
                    ph = tab_phs[node_name]
                    with ph.container():
                        if errors:
                            st.warning("\n".join(errors))
                        if node_name == "validator":
                            summary = node_output.get("validated_findings", {}).get("summary", "")
                            st.markdown(summary or "No validation output.")
                        else:
                            items = node_output.get(result_key, [])
                            if items:
                                st.markdown(items[0].get("content", ""))
                            else:
                                st.info("No results returned.")

        elapsed = time.time() - start
        st.session_state.results  = final_state
        st.session_state.results["_elapsed"] = elapsed
        st.session_state.results["_query"]   = active_query
        st.session_state.running  = False
        st.rerun()

    # ── Report ────────────────────────────────────────────────────────────────
    if res:
        elapsed = res.get("_elapsed", 0)
        report  = res.get("final_report", "No report generated.")

        st.markdown("---")
        col_title, col_time, col_md, col_pdf = st.columns([5, 2, 1, 1])
        slug = res.get("_query", "report").replace(" ", "_")
        company_name = res.get("_query", "Company")
        with col_title:
            st.markdown('<p class="section-label">Due Diligence Report</p>', unsafe_allow_html=True)
        with col_time:
            st.markdown(
                f'<p style="color:#8b949e;font-size:0.8rem;padding-top:6px">✅ Completed in {elapsed:.1f}s</p>',
                unsafe_allow_html=True,
            )
        with col_md:
            st.download_button(
                "⬇️ .md",
                data=report,
                file_name=f"{slug}_due_diligence.md",
                mime="text/markdown",
            )
        with col_pdf:
            st.download_button(
                "⬇️ PDF",
                data=_report_to_pdf(report, company_name),
                file_name=f"{slug}_due_diligence.pdf",
                mime="application/pdf",
            )

        st.markdown(report)
