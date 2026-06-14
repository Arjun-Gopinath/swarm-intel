# swarm-intel

**Multi-Agent Due Diligence Research Swarm** — built for the Microsoft Build AI Hackathon (Agent Swarms track).

Given a company name or topic, swarm-intel dispatches specialized AI agents in parallel to research news, financials, professional data, technical presence, and regulatory exposure — then cross-validates and synthesizes everything into a structured analyst brief. Optionally, a Katzilla agent pulls primary-source government data (SEC EDGAR, federal court opinions) with cryptographic citation hashes when `KATZILLA_API_KEY` is set.

---

## What it does

A single query triggers a coordinated swarm:

| Agent                    | Focus                                                              |
| ------------------------ | ------------------------------------------------------------------ |
| News Agent               | Recent news, funding, leadership changes                           |
| Financial Agent          | Revenue, valuation, funding history                                |
| LinkedIn Agent           | Headcount, leadership, team growth                                 |
| GitHub Agent             | Tech stack, OSS activity, engineering culture                      |
| Regulatory Agent         | Lawsuits, compliance risks, violations                             |
| Katzilla Agent *(opt.)* | SEC EDGAR filings + federal court opinions with citation hashes    |
| Validator Agent          | Cross-checks conflicting facts, flags gaps                         |
| Synthesizer Agent        | Produces the final 10-section analyst report                       |

---

## Architecture

```
User Query
    │
    ▼
[Orchestrator — LangGraph fan-out via Send()]
    │
    ├──► [News Agent]
    ├──► [Financial Agent]        ← run in parallel
    ├──► [LinkedIn Agent]
    ├──► [GitHub Agent]
    ├──► [Regulatory Agent]
    └──► [Katzilla Agent] (opt.)  ← SEC EDGAR + CourtListener w/ citation hashes
              │
              ▼ (all converge)
         [Validator Agent]
              │
              ▼
        [Synthesizer Agent]
              │
              ▼
         Final Report
```

Built with **LangGraph** for precise control over agent coordination and parallel execution via the `Send()` API.

Providers are swappable via environment variables — no code changes needed to switch between LLMs or search backends.

---

## Setup

### Prerequisites

- Python 3.11+
- An LLM provider (see options below)
- A search provider (see options below)

### Install

```bash
git clone https://github.com/YOUR_USERNAME/swarm-intel.git
cd swarm-intel

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install core + your chosen providers (no need to install everything)
pip install -e ".[ollama,duckduckgo]"     # zero-key default
pip install -e ".[ollama,duckduckgo,ui]"  # + Streamlit UI
pip install -e ".[claude,tavily]"         # Claude + Tavily
pip install -e ".[all]"                   # everything
```

### Configure

```bash
cp .env.example .env
# Edit .env to set your providers and any required API keys
```

---

## Provider Options

### LLM (`LLM_PROVIDER`)

| Value              | Model default              | Requires                                                   |
| ------------------ | -------------------------- | ---------------------------------------------------------- |
| `ollama` (default) | `llama3`                   | [Ollama](https://ollama.com) installed locally, no API key |
| `groq`             | `llama-3.3-70b-versatile`  | `GROQ_API_KEY` (free at [console.groq.com](https://console.groq.com)) |
| `claude`           | `claude-opus-4-8`          | `ANTHROPIC_API_KEY`                                        |
| `openai`           | `gpt-4o`                   | `OPENAI_API_KEY`                                           |

Override the model with `LLM_MODEL=<model-name>`.

**Token optimisation (Groq free tier):** Set `LLM_FAST_MODEL=llama-3.1-8b-instant` to route the 5 parallel research agents to Groq's smaller model (separate 500k tokens/day quota), reserving the 70B model for the validator and synthesizer only. If not set, all agents use `LLM_MODEL`.

### Search (`SEARCH_PROVIDER`)

| Value                  | Requires                                                         |
| ---------------------- | ---------------------------------------------------------------- |
| `duckduckgo` (default) | Nothing — no API key                                             |
| `tavily`               | `TAVILY_API_KEY` (free tier at [tavily.com](https://tavily.com)) |

### Primary Sources — Katzilla *(optional)*

Set `KATZILLA_API_KEY` to enable a 6th parallel agent that pulls from SEC EDGAR and federal court records (CourtListener) instead of web search. Each response includes a SHA-256 citation hash and a `certainty_score`.

```bash
KATZILLA_API_KEY=kz_live_...   # free tier: 1,000 calls/month — katzilla.dev
```

Best suited for US public companies. For private or non-US companies the agent returns empty results gracefully — no errors, no wasted quota.

### Zero-key quickstart (Ollama + DuckDuckGo)

```bash
# Install Ollama from https://ollama.com, then:
ollama pull llama3   # or phi3:mini for a lighter model

# .env needs nothing extra — defaults are already set
pip install -e .   # one-time, registers the CLI
swarm-intel "Stripe"
```

---

## Run

**Streamlit UI (recommended):**

```bash
streamlit run app.py
```

**CLI:**

```bash
swarm-intel "Stripe"
swarm-intel "OpenAI" --llm openai --model gpt-4o
swarm-intel "Stripe" --llm claude
swarm-intel "Stripe" --search tavily
swarm-intel "Stripe" --output report.md
```

| Flag       | Description                                                |
| ---------- | ---------------------------------------------------------- |
| `--llm`    | Override LLM provider (`ollama`, `claude`, `openai`)       |
| `--model`  | Override model name (e.g. `llama3`, `phi3:mini`, `gpt-4o`) |
| `--search` | Override search provider (`duckduckgo`, `tavily`)          |
| `--output` | Save report to a file                                      |

---

## Dependencies

| Package                      | Purpose                                 |
| ---------------------------- | --------------------------------------- |
| `langgraph`                  | Agent orchestration and graph execution |
| `langchain-community`        | Search tool adapters                    |
| `langchain-ollama`           | Ollama LLM provider                     |
| `langchain-anthropic`        | Claude LLM provider                     |
| `langchain-openai`           | OpenAI LLM provider                     |
| `duckduckgo-search` / `ddgs` | Free web search (no key)                |
| `tavily-python`              | Tavily search API                       |
| `yfinance`                   | Public company financial data           |
| `streamlit`                  | Web UI                                  |
| `pydantic`                   | State validation                        |
| `reportlab`                  | PDF report export                       |
| `python-dotenv`              | Environment config                      |

---

## Project Structure

```
swarm-intel/
├── app.py                  # Streamlit web UI
├── main.py                 # CLI entry point (registered as swarm-intel command)
├── providers.py            # LLM + search provider factory (swap via .env)
├── pyproject.toml          # package config, registers swarm-intel CLI
├── requirements.txt
├── .env.example
├── agents/
│   ├── news_agent.py
│   ├── financial_agent.py
│   ├── linkedin_agent.py
│   ├── github_agent.py
│   ├── regulatory_agent.py
│   ├── katzilla_agent.py       # optional — SEC EDGAR + CourtListener (needs KATZILLA_API_KEY)
│   ├── validator_agent.py
│   └── synthesizer_agent.py
├── graph/
│   ├── state.py            # Shared LangGraph state definition
│   └── workflow.py         # Graph wiring and fan-out logic
└── prompts/
    └── agent_prompts.py    # System prompts for each agent
```

_Built for Microsoft Build AI Hackathon — Agent Swarms track._
