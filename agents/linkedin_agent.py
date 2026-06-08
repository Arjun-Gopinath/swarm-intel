"""LinkedIn / professional intelligence agent — uses web search as proxy."""

from langchain_core.messages import SystemMessage, HumanMessage
from prompts.agent_prompts import LINKEDIN_AGENT_PROMPT
from providers import get_fast_llm, get_search


def linkedin_agent(state: dict) -> dict:
    query = state["query"]
    results = []
    errors = []

    try:
        search = get_search()

        # Two targeted searches: headcount/growth and leadership
        headcount_raw = search.invoke(f"{query} company employees headcount team size LinkedIn")[:3000]
        leadership_raw = search.invoke(f"{query} CEO founder leadership team executive")[:3000]

        llm = get_fast_llm(temperature=0)
        response = llm.invoke([
            SystemMessage(content=LINKEDIN_AGENT_PROMPT),
            HumanMessage(content=(
                f"Company: {query}\n\n"
                f"Headcount/growth search:\n{headcount_raw}\n\n"
                f"Leadership search:\n{leadership_raw}"
            )),
        ])

        results.append({
            "agent": "linkedin",
            "content": response.content,
        })

    except Exception as e:
        errors.append(f"linkedin_agent error: {str(e)}")

    return {"linkedin_results": results, "errors": errors}
