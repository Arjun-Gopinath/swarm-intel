"""CLI entry point for swarm-intel."""

import argparse
import os
import sys
from dotenv import load_dotenv

load_dotenv()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="swarm-intel",
        description="Multi-agent due diligence research swarm. Dispatches 5 specialized agents "
                    "in parallel to research a company, then validates and synthesizes a report.",
        epilog=(
            "examples:\n"
            "  python3 main.py 'Stripe'\n"
            "  python3 main.py 'OpenAI' --llm openai --model gpt-4o\n"
            "  python3 main.py 'Stripe' --llm claude --model claude-opus-4-8\n"
            "  python3 main.py 'Stripe' --search tavily\n"
            "  python3 main.py 'Stripe' --output report.md\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "query",
        type=str,
        help="Company name or research topic (e.g. 'Stripe', 'OpenAI')",
    )
    parser.add_argument(
        "--llm",
        choices=["ollama", "claude", "openai"],
        default=None,
        help="LLM provider to use. Overrides LLM_PROVIDER in .env. "
             "(default: ollama)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        metavar="MODEL_NAME",
        help="Model name for the chosen LLM provider. Overrides LLM_MODEL in .env. "
             "Examples: llama3, phi3:mini, claude-opus-4-8, gpt-4o",
    )
    parser.add_argument(
        "--search",
        choices=["duckduckgo", "tavily"],
        default=None,
        help="Search provider to use. Overrides SEARCH_PROVIDER in .env. "
             "(default: duckduckgo)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        metavar="FILE",
        help="Save the final report to a file (e.g. --output report.md)",
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Apply CLI overrides to env before importing the graph (providers read from env at call time)
    if args.llm:
        os.environ["LLM_PROVIDER"] = args.llm
    if args.model:
        os.environ["LLM_MODEL"] = args.model
    if args.search:
        os.environ["SEARCH_PROVIDER"] = args.search

    from graph.workflow import swarm

    llm_label = os.environ.get("LLM_PROVIDER", "ollama")
    model_label = os.environ.get("LLM_MODEL", "")
    search_label = os.environ.get("SEARCH_PROVIDER", "duckduckgo")

    print(f"\nswarm-intel — researching: {args.query}")
    print(f"LLM: {llm_label}{f'/{model_label}' if model_label else ''}  |  Search: {search_label}\n")
    print("Dispatching agents in parallel...\n")

    result = swarm.invoke({
        "query": args.query,
        "news_results": [],
        "financial_results": [],
        "linkedin_results": [],
        "github_results": [],
        "regulatory_results": [],
        "errors": [],
    })

    if result.get("errors"):
        print("Warnings:")
        for err in result["errors"]:
            print(f"  - {err}")
        print()

    report = result.get("final_report", "No report generated.")

    print("=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(report)

    if args.output:
        with open(args.output, "w") as f:
            f.write(f"# Due Diligence Report: {args.query}\n\n")
            f.write(report)
        print(f"\nReport saved to {args.output}")


if __name__ == "__main__":
    main()
