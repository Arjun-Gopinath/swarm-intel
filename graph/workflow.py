"""LangGraph workflow wiring all swarm agents together."""

from langgraph.graph import StateGraph, END
from langgraph.constants import Send

from graph.state import ResearchState
from agents.news_agent import news_agent
from agents.financial_agent import financial_agent
from agents.linkedin_agent import linkedin_agent
from agents.github_agent import github_agent
from agents.regulatory_agent import regulatory_agent
from agents.validator_agent import validator_agent
from agents.synthesizer_agent import synthesizer_agent


def dispatch_agents(state: ResearchState):
    """Fan-out: send the query to all research agents in parallel."""
    query = state["query"]
    return [
        Send("news_agent", {"query": query}),
        Send("financial_agent", {"query": query}),
        Send("linkedin_agent", {"query": query}),
        Send("github_agent", {"query": query}),
        Send("regulatory_agent", {"query": query}),
    ]


def build_graph() -> StateGraph:
    graph = StateGraph(ResearchState)

    # Research agents (run in parallel via fan-out)
    graph.add_node("news_agent", news_agent)
    graph.add_node("financial_agent", financial_agent)
    graph.add_node("linkedin_agent", linkedin_agent)
    graph.add_node("github_agent", github_agent)
    graph.add_node("regulatory_agent", regulatory_agent)

    # Downstream agents
    graph.add_node("validator", validator_agent)
    graph.add_node("synthesizer", synthesizer_agent)

    # Fan-out from START to all research agents in parallel
    graph.add_conditional_edges("__start__", dispatch_agents)

    # All research agents feed into the validator
    for agent in ["news_agent", "financial_agent", "linkedin_agent", "github_agent", "regulatory_agent"]:
        graph.add_edge(agent, "validator")

    graph.add_edge("validator", "synthesizer")
    graph.add_edge("synthesizer", END)

    return graph.compile()


swarm = build_graph()
