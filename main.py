"""CLI entry point for swarm-intel."""

import argparse
from dotenv import load_dotenv

load_dotenv()

from graph.workflow import swarm


def main():
    parser = argparse.ArgumentParser(description="swarm-intel: Multi-Agent Due Diligence Swarm")
    parser.add_argument("query", type=str, help="Company name or research topic")
    args = parser.parse_args()

    print(f"\n🕵️  swarm-intel starting research on: {args.query}\n")
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
        print("⚠️  Warnings:")
        for err in result["errors"]:
            print(f"  - {err}")
        print()

    print("=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(result.get("final_report", "No report generated."))


if __name__ == "__main__":
    main()
