"""Validator agent — cross-checks and reconciles all agent outputs."""

from langchain_core.messages import SystemMessage, HumanMessage
from prompts.agent_prompts import VALIDATOR_AGENT_PROMPT
from providers import get_llm, friendly_error
import json


def _primary_content(items: list) -> str:
    """Extract the primary synthesized content from an agent's result list."""
    for item in items:
        if isinstance(item, dict) and item.get("content"):
            return item["content"]
    return "No findings."


def validator_agent(state: dict) -> dict:
    errors = []

    try:
        findings = {
            "news": state.get("news_results", []),
            "financial": state.get("financial_results", []),
            "linkedin": state.get("linkedin_results", []),
            "github": state.get("github_results", []),
            "regulatory": state.get("regulatory_results", []),
            "primary_source": state.get("primary_source_results", []),
        }

        # Pass only the primary synthesized content per agent — each agent's LLM
        # already distilled the raw search results, so this is the actual finding,
        # not a truncation. Full findings stay in state for the synthesizer.
        validator_input = {k: _primary_content(v) for k, v in findings.items()}

        llm = get_llm(temperature=0)
        response = llm.invoke([
            SystemMessage(content=VALIDATOR_AGENT_PROMPT),
            HumanMessage(content=f"All agent findings:\n{json.dumps(validator_input, indent=2, default=str)}"),
        ])

        validated = {
            "summary": response.content,
            "agent_summaries": validator_input,  # content-only, raw_sources excluded
            "agent_errors": state.get("errors", []),
        }

    except Exception as e:
        errors.append(f"validator_agent error: {friendly_error(e)}")
        # Still pass agent_summaries so the synthesizer has data even if validation failed
        fallback_input = {
            k: _primary_content(state.get(f"{k}_results", []))
            for k in ("news", "financial", "linkedin", "github", "regulatory", "primary_source")
        }
        validated = {"summary": "Validation failed — proceeding with raw findings.", "agent_summaries": fallback_input, "agent_errors": errors}

    return {"validated_findings": validated, "errors": errors}
