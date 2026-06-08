# 🕵️ swarm-intel

**Multi-Agent Due Diligence Research Swarm** — built for the Microsoft Build AI Hackathon (Agent Swarms track).

Given a company name or topic, swarm-intel dispatches 5 specialized AI agents in parallel to research news, financials, professional data, technical presence, and regulatory exposure — then cross-validates and synthesizes everything into a structured analyst brief in under 2 minutes.

---

## What it does

A single query triggers a coordinated swarm:

| Agent                | Data Source         | Focus                                         |
| -------------------- | ------------------- | --------------------------------------------- |
| 📰 News Agent        | Tavily Search       | Recent news, funding, leadership changes      |
| 💰 Financial Agent   | yFinance + Tavily   | Revenue, valuation, funding history           |
| 👥 LinkedIn Agent    | Tavily (web proxy)  | Headcount, leadership, team growth            |
| 💻 GitHub Agent      | GitHub API + Tavily | Tech stack, OSS activity, engineering culture |
| ⚖️ Regulatory Agent  | Tavily Search       | Lawsuits, compliance risks, violations        |
| ✅ Validator Agent   | GPT-4o              | Cross-checks conflicting facts, flags gaps    |
| 📋 Synthesizer Agent | GPT-4o              | Produces the final 10-section analyst report  |

---

## Architecture

```
User Query
    │
    ▼
[Orchestrator — LangGraph fan-out via Send()]
    │
    ├──► [News Agent]
    ├──► [Financial Agent]     ← run in parallel
    ├──► [LinkedIn Agent]
    ├──► [GitHub Agent]
    └──► [Regulatory Agent]
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

---

## Setup

### Prerequisites

- Python 3.11+
- OpenAI API key
- Tavily API key (free tier at [tavily.com](https://tavily.com))

### Install

```bash
git clone https://github.com/YOUR_USERNAME/swarm-intel.git
cd swarm-intel

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### Run

**Streamlit UI (recommended):**

```bash
streamlit run app.py
```

**CLI:**

```bash
python main.py "OpenAI"
python main.py "Stripe"
```

---

## Dependencies

| Package               | Version | Purpose                                 |
| --------------------- | ------- | --------------------------------------- |
| `langgraph`           | ≥0.2.0  | Agent orchestration and graph execution |
| `langchain-openai`    | ≥0.2.0  | GPT-4o integration                      |
| `langchain-community` | ≥0.3.0  | Tavily search tool                      |
| `tavily-python`       | ≥0.3.0  | Web search API                          |
| `yfinance`            | ≥0.2.0  | Public company financial data           |
| `streamlit`           | ≥1.39.0 | Web UI                                  |
| `pydantic`            | ≥2.0.0  | State validation                        |
| `reportlab`           | ≥4.0.0  | PDF report export                       |
| `python-dotenv`       | ≥1.0.0  | Environment config                      |

---

## AI Tools Used

- **GPT-4o** (OpenAI) — powers all 7 agents for reasoning, extraction, validation, and synthesis
- **Tavily Search API** — real-time web search used by 5 agents
- **GitHub REST API** — technical intelligence (unauthenticated or with `GITHUB_TOKEN`)
- **Yahoo Finance API** — public company financial data via `yfinance`
- **LangGraph** — orchestration framework managing parallel agent execution and shared state

---

## Project Structure

```
swarm-intel/
├── app.py                  # Streamlit web UI
├── main.py                 # CLI entry point
├── requirements.txt
├── .env.example
├── agents/
│   ├── news_agent.py
│   ├── financial_agent.py
│   ├── linkedin_agent.py
│   ├── github_agent.py
│   ├── regulatory_agent.py
│   ├── validator_agent.py
│   └── synthesizer_agent.py
├── graph/
│   ├── state.py            # Shared LangGraph state definition
│   └── workflow.py         # Graph wiring and fan-out logic
├── prompts/
│   └── agent_prompts.py    # System prompts for each agent
└── output/                 # Generated reports saved here
```

_Built for Microsoft Build AI Hackathon — Agent Swarms track._
