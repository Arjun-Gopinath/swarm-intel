"""Shared state definition for the swarm-intel LangGraph workflow."""

from typing import Annotated, Any
from typing_extensions import TypedDict
import operator


class ResearchState(TypedDict):
    """State shared across all agents in the swarm."""

    # Input
    query: str                          # Company name or research topic

    # Parallel agent outputs (aggregated via operator.add)
    news_results: Annotated[list[dict], operator.add]
    financial_results: Annotated[list[dict], operator.add]
    linkedin_results: Annotated[list[dict], operator.add]
    github_results: Annotated[list[dict], operator.add]
    regulatory_results: Annotated[list[dict], operator.add]

    # Downstream
    validated_findings: dict[str, Any]  # Validator output
    final_report: str                   # Synthesizer output
    errors: Annotated[list[str], operator.add]  # Any agent errors
