"""Read a paper book and print the rule breaches."""

from __future__ import annotations

import argparse
from pathlib import Path

from risksentinel import __version__
from risksentinel.agent import RiskAgent, demo_snapshot, load_snapshot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="risksentinel",
        description="Risk rules for a paper book. Not financial advice. No orders.",
    )
    parser.add_argument("--version", action="version", version=f"risksentinel {__version__}")
    parser.add_argument("--demo", action="store_true", help="Review a book that breaches the default rules")
    parser.add_argument("--json", help="Path to a snapshot JSON file")
    parser.add_argument("--max-weight", type=float, default=0.25)
    parser.add_argument("--max-loss", type=float, default=0.08)
    parser.add_argument("--min-cash", type=float, default=0.10)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.demo and not args.json:
        build_parser().print_help()
        return 0
    try:
        agent = RiskAgent(args.max_weight, args.max_loss, args.min_cash)
        snapshot = demo_snapshot() if args.demo else load_snapshot(Path(args.json).read_text())
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 2
    print(agent.report(snapshot))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
