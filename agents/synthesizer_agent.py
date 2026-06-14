"""Synthesizer agent — produces the final structured due diligence report."""

from langchain_core.messages import SystemMessage, HumanMessage
from prompts.agent_prompts import SYNTHESIZER_AGENT_PROMPT
from providers import get_llm, friendly_error
import json


def synthesizer_agent(state: dict) -> dict:
    errors = []

    try:
        validated  = state.get("validated_findings", {})
        query      = state.get("query", "Unknown company")
        summaries  = validated.get("agent_summaries", {})
        validation = validated.get("summary", "")

        # Fallback: if validator passed nothing, read agent results directly from state
        if not summaries:
            from agents.validator_agent import _primary_content
            summaries = {
                k: _primary_content(state.get(f"{k}_results", []))
                for k in ("news", "financial", "linkedin", "github", "regulatory", "primary_source")
            }

        # Extract citations from Katzilla results and pass them separately so the
        # synthesizer can render a Primary Sources section with hashes intact
        citations = []
        for item in state.get("primary_source_results", []):
            if isinstance(item, dict):
                citations.extend(item.get("citations", []))

        citations_block = ""
        if citations:
            lines = [f"  - {c['source']} | {c['url']} | hash: {c['hash']}" for c in citations]
            citations_block = "\n\nPrimary source citations (include in section 11):\n" + "\n".join(lines)

        llm = get_llm(temperature=0.2)
        response = llm.invoke([
            SystemMessage(content=SYNTHESIZER_AGENT_PROMPT),
            HumanMessage(content=(
                f"Research subject: {query}\n\n"
                f"Validation notes:\n{validation}\n\n"
                f"Agent findings:\n{json.dumps(summaries, indent=2, default=str)}"
                f"{citations_block}"
            )),
        ])

        report = response.content

    except Exception as e:
        msg = friendly_error(e)
        errors.append(f"synthesizer_agent error: {msg}")
        report = f"Report generation failed: {msg}"

    return {"final_report": report, "errors": errors}
