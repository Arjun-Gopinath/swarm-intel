# swarm-intel — Claude Code Guide

## What this project is

A multi-agent due diligence research swarm built with LangGraph. Given a company name, it fans out 5 research agents in parallel, then validates and synthesizes the results into a structured analyst report.

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
LLM_PROVIDER=ollama          # ollama | claude | openai
LLM_MODEL=llama3             # optional model override
SEARCH_PROVIDER=duckduckgo   # duckduckgo | tavily
```

The factory lives in `providers.py`. To add a new provider, add a branch to `get_llm()` or `get_search()` there — agents never import provider libraries directly.

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
    raw = search.invoke("...")
    llm = get_llm(temperature=0)
    response = llm.invoke([SystemMessage(...), HumanMessage(...)])
    return {"<result_key>": [...], "errors": [...]}
```

Validator and synthesizer agents use only `get_llm()` (no search).

## LangGraph flow

1. `__start__` → `dispatch_agents()` fans out via `Send()` to all 5 research agents in parallel
2. All 5 converge into `validator`
3. `validator` → `synthesizer` → `END`

## Adding a new agent

1. Create `agents/your_agent.py` following the pattern above
2. Add a system prompt to `prompts/agent_prompts.py`
3. Add a result key to `graph/state.py`
4. Register the node and wire its edges in `graph/workflow.py`
5. Add it to the `dispatch_agents()` fan-out (if it should run in parallel) or chain it after the validator
