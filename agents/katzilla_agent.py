"""Katzilla agent — pulls primary-source government data (SEC EDGAR, CourtListener).

Requires KATZILLA_API_KEY in .env. When the key is absent the agent returns empty
results and the swarm runs exactly as before (graceful no-op).
"""

from langchain_core.messages import SystemMessage, HumanMessage
from prompts.agent_prompts import KATZILLA_AGENT_PROMPT
from providers import get_katzilla, get_fast_llm, friendly_error


def katzilla_agent(state: dict) -> dict:
    kz = get_katzilla()
    if kz is None:
        return {"primary_source_results": [], "errors": []}

    company = state["query"]
    findings = []
    errors = []

    queries = [
        ("government", "sec-edgar",    {"query": company, "forms": "10-K,10-Q,8-K", "limit": 5}),
        ("crime",      "courtlistener", {"query": company, "limit": 5}),
    ]

    for agent_id, action_id, params in queries:
        try:
            result = kz.query(agent_id, action_id, params)
            if result.get("success"):
                # data is a nested dict; find the first list value (e.g. "filings" or "opinions")
                inner = result["data"]
                records = next((v for v in inner.values() if isinstance(v, list)), []) if isinstance(inner, dict) else inner
                data_str = str(records)[:1500]
                findings.append({
                    "source":       result["citation"]["source_name"],
                    "url":          result["citation"]["source_url"],
                    "retrieved_at": result["citation"]["retrieved_at"],
                    "hash":         result["citation"]["data_hash"],
                    "certainty":    result["quality"]["certainty_score"],
                    "data":         data_str,
                })
        except Exception as e:
            errors.append(f"Katzilla {agent_id}/{action_id}: {friendly_error(e)}")

    if not findings:
        return {"primary_source_results": [], "errors": errors}

    llm = get_fast_llm(temperature=0)
    response = llm.invoke([
        SystemMessage(content=KATZILLA_AGENT_PROMPT),
        HumanMessage(content=f"Company: {company}\n\nPrimary source data:\n{str(findings)[:3000]}"),
    ])

    return {
        "primary_source_results": [{
            "content":   response.content,
            "citations": [{"source": f["source"], "hash": f["hash"], "url": f["url"]} for f in findings],
        }],
        "errors": errors,
    }
