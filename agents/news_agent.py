"""News research agent — searches recent news about a company or topic."""

from langchain_core.messages import SystemMessage, HumanMessage
from prompts.agent_prompts import NEWS_AGENT_PROMPT
from providers import get_fast_llm, get_search


def news_agent(state: dict) -> dict:
    query = state["query"]
    results = []
    errors = []

    try:
        search = get_search()
        raw = search.invoke(f"{query} company news 2024 2025")[:3000]

        llm = get_fast_llm(temperature=0)
        response = llm.invoke([
            SystemMessage(content=NEWS_AGENT_PROMPT),
            HumanMessage(content=f"Company/topic: {query}\n\nRaw search results:\n{raw}"),
        ])

        results.append({
            "agent": "news",
            "content": response.content,
            "raw_sources": raw,
        })

    except Exception as e:
        errors.append(f"news_agent error: {str(e)}")

    return {"news_results": results, "errors": errors}
