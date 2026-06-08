"""Validator agent — cross-checks and reconciles all agent outputs."""

from langchain_core.messages import SystemMessage, HumanMessage
from prompts.agent_prompts import VALIDATOR_AGENT_PROMPT
from providers import get_llm
import json


def validator_agent(state: dict) -> dict:
    errors = []

    try:
        findings = {
            "news": state.get("news_results", []),
            "financial": state.get("financial_results", []),
            "linkedin": state.get("linkedin_results", []),
            "github": state.get("github_results", []),
            "regulatory": state.get("regulatory_results", []),
        }

        llm = get_llm(temperature=0)
        response = llm.invoke([
            SystemMessage(content=VALIDATOR_AGENT_PROMPT),
            HumanMessage(content=f"All agent findings:\n{json.dumps(findings, indent=2, default=str)}"),
        ])

        validated = {
            "summary": response.content,
            "raw_findings": findings,
            "agent_errors": state.get("errors", []),
        }

    except Exception as e:
        errors.append(f"validator_agent error: {str(e)}")
        validated = {"summary": "Validation failed.", "raw_findings": {}, "agent_errors": errors}

    return {"validated_findings": validated, "errors": errors}
