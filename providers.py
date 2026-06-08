"""Provider factory — returns LLM and search instances based on environment config.

LLM_PROVIDER: ollama (default) | claude | openai
LLM_MODEL:    model name override (e.g. llama3, claude-opus-4-8, gpt-4o)
SEARCH_PROVIDER: duckduckgo (default) | tavily
"""

import os


def get_llm(temperature: float = 0):
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    model_override = os.getenv("LLM_MODEL")

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=model_override or "llama3", temperature=temperature)

    if provider == "claude":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model_override or "claude-opus-4-8", temperature=temperature)

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model_override or "gpt-4o", temperature=temperature)

    raise ValueError(f"Unknown LLM_PROVIDER '{provider}'. Choose: ollama, claude, openai")


def get_search():
    provider = os.getenv("SEARCH_PROVIDER", "duckduckgo").lower()

    if provider == "duckduckgo":
        from langchain_community.tools import DuckDuckGoSearchRun
        return DuckDuckGoSearchRun()

    if provider == "tavily":
        from langchain_community.tools.tavily_search import TavilySearchResults
        return TavilySearchResults(max_results=5)

    raise ValueError(f"Unknown SEARCH_PROVIDER '{provider}'. Choose: duckduckgo, tavily")
