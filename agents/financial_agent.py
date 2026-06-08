"""Financial data agent — retrieves financials via yfinance (public) and web search (private)."""

import yfinance as yf
from langchain_core.messages import SystemMessage, HumanMessage
from prompts.agent_prompts import FINANCIAL_AGENT_PROMPT
from providers import get_fast_llm, get_search


def financial_agent(state: dict) -> dict:
    query = state["query"]
    results = []
    errors = []

    try:
        # Try fetching as a public ticker first
        ticker_data = {}
        try:
            ticker = yf.Ticker(query)
            info = ticker.info
            if info.get("regularMarketPrice"):
                ticker_data = {
                    "market_cap": info.get("marketCap"),
                    "revenue": info.get("totalRevenue"),
                    "price": info.get("regularMarketPrice"),
                    "sector": info.get("sector"),
                    "employees": info.get("fullTimeEmployees"),
                }
        except Exception:
            pass  # Not a public ticker, fall through to web search

        # Web search for financial context (works for private companies too)
        search = get_search()
        raw = search.invoke(f"{query} funding valuation revenue financials")[:3000]

        llm = get_fast_llm(temperature=0)
        response = llm.invoke([
            SystemMessage(content=FINANCIAL_AGENT_PROMPT),
            HumanMessage(content=(
                f"Company: {query}\n\n"
                f"Public market data: {ticker_data or 'Not a public company or ticker not found'}\n\n"
                f"Web search results:\n{raw}"
            )),
        ])

        results.append({
            "agent": "financial",
            "content": response.content,
            "ticker_data": ticker_data,
        })

    except Exception as e:
        errors.append(f"financial_agent error: {str(e)}")

    return {"financial_results": results, "errors": errors}
