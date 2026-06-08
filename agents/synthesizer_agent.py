"""Synthesizer agent — produces the final structured due diligence report."""

from langchain_core.messages import SystemMessage, HumanMessage
from prompts.agent_prompts import SYNTHESIZER_AGENT_PROMPT
from providers import get_llm
import json


def synthesizer_agent(state: dict) -> dict:
    errors = []

    try:
        validated = state.get("validated_findings", {})
        query = state.get("query", "Unknown company")

        llm = get_llm(temperature=0.2)
        response = llm.invoke([
            SystemMessage(content=SYNTHESIZER_AGENT_PROMPT),
            HumanMessage(content=(
                f"Research subject: {query}\n\n"
                f"Validated findings:\n{json.dumps(validated, indent=2, default=str)}"
            )),
        ])

        report = response.content

    except Exception as e:
        errors.append(f"synthesizer_agent error: {str(e)}")
        report = f"Report generation failed: {str(e)}"

    return {"final_report": report, "errors": errors}
