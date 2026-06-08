"""Regulatory and legal exposure agent."""

from langchain_core.messages import SystemMessage, HumanMessage
from prompts.agent_prompts import REGULATORY_AGENT_PROMPT
from providers import get_fast_llm, get_search


def regulatory_agent(state: dict) -> dict:
    query = state["query"]
    results = []
    errors = []

    try:
        search = get_search()

        legal_raw = search.invoke(f"{query} lawsuit litigation legal regulatory violation fine")[:3000]
        compliance_raw = search.invoke(f"{query} GDPR CCPA data breach privacy compliance")[:3000]

        llm = get_fast_llm(temperature=0)
        response = llm.invoke([
            SystemMessage(content=REGULATORY_AGENT_PROMPT),
            HumanMessage(content=(
                f"Company: {query}\n\n"
                f"Legal/litigation search:\n{legal_raw}\n\n"
                f"Compliance search:\n{compliance_raw}"
            )),
        ])

        results.append({
            "agent": "regulatory",
            "content": response.content,
        })

    except Exception as e:
        errors.append(f"regulatory_agent error: {str(e)}")

    return {"regulatory_results": results, "errors": errors}
