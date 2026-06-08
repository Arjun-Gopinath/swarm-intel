"""Provider factory — LLM and search instances resolved from environment config.

LLM_PROVIDER:    ollama (default) | groq | claude | openai
LLM_MODEL:       optional model name override
SEARCH_PROVIDER: duckduckgo (default) | tavily

To add a new provider: add one entry to LLM_REGISTRY or SEARCH_REGISTRY.
"""

import os
from typing import Callable


# ── LLM registry ──────────────────────────────────────────────────────────────

def _ollama(temperature: float):
    from langchain_ollama import ChatOllama
    return ChatOllama(model=os.getenv("LLM_MODEL", "llama3"), temperature=temperature)

def _groq(temperature: float):
    from langchain_groq import ChatGroq
    return ChatGroq(model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"), temperature=temperature)

def _claude(temperature: float):
    from langchain_anthropic import ChatAnthropic
    return ChatAnthropic(model=os.getenv("LLM_MODEL", "claude-opus-4-8"), temperature=temperature)

def _openai(temperature: float):
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model=os.getenv("LLM_MODEL", "gpt-4o"), temperature=temperature)

LLM_REGISTRY: dict[str, Callable[[float], object]] = {
    "ollama": _ollama,
    "groq":   _groq,
    "claude": _claude,
    "openai": _openai,
}


# ── Search registry ───────────────────────────────────────────────────────────

def _duckduckgo():
    from langchain_community.tools import DuckDuckGoSearchRun
    return DuckDuckGoSearchRun()

def _tavily():
    from langchain_community.tools.tavily_search import TavilySearchResults
    return TavilySearchResults(max_results=5)

SEARCH_REGISTRY: dict[str, Callable[[], object]] = {
    "duckduckgo": _duckduckgo,
    "tavily":     _tavily,
}


# ── Public API ────────────────────────────────────────────────────────────────

def get_llm(temperature: float = 0):
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider not in LLM_REGISTRY:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider}'. "
            f"Available: {', '.join(LLM_REGISTRY)}"
        )
    return LLM_REGISTRY[provider](temperature)


def get_search():
    provider = os.getenv("SEARCH_PROVIDER", "duckduckgo").lower()
    if provider not in SEARCH_REGISTRY:
        raise ValueError(
            f"Unknown SEARCH_PROVIDER '{provider}'. "
            f"Available: {', '.join(SEARCH_REGISTRY)}"
        )
    return SEARCH_REGISTRY[provider]()
