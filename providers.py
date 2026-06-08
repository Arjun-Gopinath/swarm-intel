"""Provider factory — LLM and search instances resolved from environment config.

LLM_PROVIDER:    ollama (default) | groq | claude | openai
LLM_MODEL:       optional model name override
SEARCH_PROVIDER: duckduckgo (default) | tavily

To add a new provider: add one entry to LLM_REGISTRY or SEARCH_REGISTRY.
"""

import os
import re
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


def get_fast_llm(temperature: float = 0):
    """Return a smaller/cheaper model for high-volume research agents.

    If LLM_FAST_MODEL is not set, falls back to get_llm() — no behaviour change
    for users who don't need quota splitting.
    Set LLM_FAST_MODEL=llama-3.1-8b-instant in .env to split Groq quotas.
    """
    fast_model = os.getenv("LLM_FAST_MODEL")
    if not fast_model:
        return get_llm(temperature)
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider not in LLM_REGISTRY:
        return get_llm(temperature)
    original = os.environ.get("LLM_MODEL")
    os.environ["LLM_MODEL"] = fast_model
    try:
        llm = LLM_REGISTRY[provider](temperature)
    finally:
        if original is None:
            os.environ.pop("LLM_MODEL", None)
        else:
            os.environ["LLM_MODEL"] = original
    return llm


def friendly_error(e: Exception) -> str:
    """Return a human-readable message for common API errors."""
    msg = str(e)
    if "429" in msg or "rate_limit_exceeded" in msg:
        # Try to extract retry time from Groq's error message
        match = re.search(r"Please try again in ([\w.]+)", msg)
        retry = f" Please try again in {match.group(1)}." if match else ""
        if "tokens per day" in msg:
            return f"Daily token limit reached on the free tier.{retry}"
        if "tokens per minute" in msg:
            return f"Per-minute token limit reached.{retry}"
        return f"Rate limit reached.{retry}"
    if "413" in msg:
        return "Request too large for the model. Try a shorter query."
    return msg
