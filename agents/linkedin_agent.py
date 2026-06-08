"""LinkedIn / professional intelligence agent — uses web search as proxy."""

from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import SystemMessage, HumanMessage
from prompts.agent_prompts import LINKEDIN_AGENT_PROMPT


def linkedin_agent(state: dict) -> dict:
    query = state["query"]
    results = []
    errors = []

    try:
        search = TavilySearchResults(max_results=5)

        # Two targeted searches: headcount/growth and leadership
        headcount_raw = search.invoke(f"{query} company employees headcount team size LinkedIn")
        leadership_raw = search.invoke(f"{query} CEO founder leadership team executive")

        llm = ChatOpenAI(model="gpt-4o", temperature=0)
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
