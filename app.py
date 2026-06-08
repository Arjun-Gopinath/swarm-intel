"""Streamlit UI for swarm-intel — Multi-Agent Due Diligence Swarm."""

import streamlit as st
from dotenv import load_dotenv
import time

load_dotenv()

from graph.workflow import swarm

st.set_page_config(
    page_title="swarm-intel",
    page_icon="🕵️",
    layout="wide",
)

st.title("🕵️ swarm-intel")
st.caption("Multi-Agent Due Diligence Research Swarm · Built for Microsoft Build AI Hackathon")

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    query = st.text_input(
        "Company or topic to research",
        placeholder="e.g. OpenAI, Stripe, Perplexity AI",
        help="Enter a company name or research topic. The swarm will run 5 agents in parallel.",
    )

with col2:
    st.markdown("**Agents in the swarm**")
    agents = ["📰 News", "💰 Financial", "👥 LinkedIn", "💻 GitHub", "⚖️ Regulatory"]
    for a in agents:
        st.markdown(f"- {a}")

run = st.button("🚀 Run Swarm", type="primary", disabled=not bool(query))

if run and query:
    st.divider()

    # Show live agent status
    status_cols = st.columns(5)
    agent_labels = ["📰 News", "💰 Financial", "👥 LinkedIn", "💻 GitHub", "⚖️ Regulatory"]
    placeholders = [col.empty() for col in status_cols]

    for i, (ph, label) in enumerate(zip(placeholders, agent_labels)):
        ph.status(label, state="running")

    with st.spinner("Swarm running — agents researching in parallel..."):
        start = time.time()
        result = swarm.invoke({"query": query, "news_results": [], "financial_results": [],
                               "linkedin_results": [], "github_results": [], "regulatory_results": [],
                               "errors": []})
        elapsed = time.time() - start

    # Update agent statuses to complete
    for ph, label in zip(placeholders, agent_labels):
        ph.status(label, state="complete")

    st.success(f"✅ Research complete in {elapsed:.1f}s")

    # Show errors if any
    if result.get("errors"):
        with st.expander("⚠️ Agent warnings", expanded=False):
            for err in result["errors"]:
                st.warning(err)

    st.divider()

    # Final report
    st.subheader("📋 Due Diligence Report")
    st.markdown(result.get("final_report", "No report generated."))

    st.divider()

    # Raw agent outputs in expanders
    st.subheader("🔍 Agent Outputs")

    tab_news, tab_fin, tab_li, tab_gh, tab_reg, tab_val = st.tabs([
        "News", "Financial", "LinkedIn", "GitHub", "Regulatory", "Validator"
    ])

    def _show_results(tab, results_key):
        with tab:
            items = result.get(results_key, [])
            if items:
                st.markdown(items[0].get("content", "No output."))
            else:
                st.info("No results from this agent.")

    _show_results(tab_news, "news_results")
    _show_results(tab_fin, "financial_results")
    _show_results(tab_li, "linkedin_results")
    _show_results(tab_gh, "github_results")
    _show_results(tab_reg, "regulatory_results")

    with tab_val:
        validated = result.get("validated_findings", {})
        st.markdown(validated.get("summary", "No validation output."))

    # Download report
    st.divider()
    st.download_button(
        "⬇️ Download Report (txt)",
        data=result.get("final_report", ""),
        file_name=f"{query.replace(' ', '_')}_due_diligence.txt",
        mime="text/plain",
    )
