# swarm-intel — Claude Code Guide

## What this project is

A multi-agent due diligence research swarm built with LangGraph. Given a company name, it fans out research agents in parallel, then validates and synthesizes the results into a structured analyst report. A Katzilla agent pulls primary-source government data (SEC EDGAR, CourtListener) when `KATZILLA_API_KEY` is set.

## How to run

After cloning, install only the providers you need:

```bash
pip install -e ".[ollama,duckduckgo]"     # zero-key default
pip install -e ".[ollama,duckduckgo,ui]"  # + Streamlit UI
pip install -e ".[claude,tavily]"         # Claude + Tavily
pip install -e ".[all]"                   # everything
```

Then run from anywhere:

```bash
# CLI
swarm-intel "Stripe"
swarm-intel "Stripe" --llm claude --model claude-opus-4-8
swarm-intel "Stripe" --search tavily --output report.md

# Streamlit UI
streamlit run app.py
```

## Provider configuration

All provider switching is done via `.env` — no code changes needed.

```bash
LLM_PROVIDER=ollama          # ollama | groq | claude | openai
LLM_MODEL=llama3             # optional model override
LLM_FAST_MODEL=              # optional — smaller model for research agents only
                             # e.g. llama-3.1-8b-instant on Groq splits the daily quota
SEARCH_PROVIDER=duckduckgo   # duckduckgo | tavily
KATZILLA_API_KEY=            # optional — enables primary-source SEC/court data. See [here](https://katzilla.dev/docs)
```

The factory lives in `providers.py`. To add a new provider, add a branch to `get_llm()` or `get_search()` there — agents never import provider libraries directly.

`get_fast_llm()` is used by all 5 research agents. If `LLM_FAST_MODEL` is not set it falls back to `get_llm()` — no behaviour change. Set it to route high-volume research calls to a cheaper model while keeping the quality model for validator and synthesizer.

## Architecture

```
pyproject.toml      — package config, registers `swarm-intel` as a CLI command
main.py             — CLI entry point (argparse), reads flags and invokes the swarm
providers.py        — get_llm(temperature) / get_search() factory
graph/workflow.py   — LangGraph graph wiring, fan-out via Send()
graph/state.py      — ResearchState TypedDict (shared across all agents)
agents/             — one file per agent, all follow the same pattern
prompts/            — system prompts kept separate from agent logic
```

## Agent pattern

Every research agent follows this structure:

```python
def some_agent(state: dict) -> dict:
    search = get_search()
    raw = search.invoke("...")[:3000]   # cap search input to control token usage
    llm = get_fast_llm(temperature=0)  # uses smaller model if LLM_FAST_MODEL is set
    response = llm.invoke([SystemMessage(...), HumanMessage(...)])
    return {"<result_key>": [...], "errors": [...]}
```

Validator and synthesizer agents use `get_llm()` (quality model, no search).

## LangGraph flow

1. `__start__` → `dispatch_agents()` fans out via `Send()` to all research agents in parallel
2. All agents converge into `validator`
3. `validator` → `synthesizer` → `END`

## Adding a new agent

1. Create `agents/your_agent.py` following the pattern above
2. Add a system prompt to `prompts/agent_prompts.py`
3. Add a result key to `graph/state.py`
4. Register the node and wire its edges in `graph/workflow.py`
5. Add it to the `dispatch_agents()` fan-out (if it should run in parallel) or chain it after the validator
