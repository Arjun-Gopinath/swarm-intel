"""GitHub technical intelligence agent — uses GitHub API + web search."""

import requests
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import SystemMessage, HumanMessage
from prompts.agent_prompts import GITHUB_AGENT_PROMPT
import os


GITHUB_API = "https://api.github.com"


def _fetch_github_org(org_name: str) -> dict:
    """Try to fetch org data from GitHub API (unauthenticated, rate-limited)."""
    headers = {}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        org = requests.get(f"{GITHUB_API}/orgs/{org_name}", headers=headers, timeout=5).json()
        repos = requests.get(f"{GITHUB_API}/orgs/{org_name}/repos?sort=stars&per_page=5", headers=headers, timeout=5).json()
        return {"org": org, "top_repos": repos if isinstance(repos, list) else []}
    except Exception:
        return {}


def github_agent(state: dict) -> dict:
    query = state["query"]
    results = []
    errors = []

    try:
        # Guess org slug (lowercase, no spaces)
        org_slug = query.lower().replace(" ", "").replace(".", "")
        github_data = _fetch_github_org(org_slug)

        search = TavilySearchResults(max_results=4)
        web_raw = search.invoke(f"{query} GitHub open source tech stack engineering")

        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        response = llm.invoke([
            SystemMessage(content=GITHUB_AGENT_PROMPT),
            HumanMessage(content=(
                f"Company: {query}\n\n"
                f"GitHub API data (org slug tried: {org_slug}):\n{github_data or 'Not found'}\n\n"
                f"Web search results:\n{web_raw}"
            )),
        ])

        results.append({
            "agent": "github",
            "content": response.content,
            "github_data": github_data,
        })

    except Exception as e:
        errors.append(f"github_agent error: {str(e)}")

    return {"github_results": results, "errors": errors}
