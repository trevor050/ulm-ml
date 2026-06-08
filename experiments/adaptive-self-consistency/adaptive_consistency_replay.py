"""Replay adaptive self-consistency policies on cached answer-only traces."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from ulm_ml.adaptive_consistency import (
    evaluate_trace_policy,
    fixed_budget_rule,
    load_answer_trace_csv,
    posterior_confidence_rule,
    vote_margin_rule,
)
from ulm_ml.paths import REPORTS_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace_csv", type=Path)
    parser.add_argument("--max-samples", type=int, default=32)
    parser.add_argument("--min-samples", type=int, default=4)
    parser.add_argument("--posterior-draws", type=int, default=2048)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPORTS_DIR / "adaptive-consistency-replay.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = load_answer_trace_csv(args.trace_csv)
    policies = [
        ("fixed-8", lambda: fixed_budget_rule(min(8, args.max_samples))),
        ("fixed-max", lambda: fixed_budget_rule(args.max_samples)),
        (
            "margin-3",
            lambda: vote_margin_rule(
                min_samples=args.min_samples,
                margin=3,
                max_samples=args.max_samples,
            ),
        ),
        (
            "posterior-0.90",
            lambda: posterior_confidence_rule(
                min_samples=args.min_samples,
                confidence=0.90,
                max_samples=args.max_samples,
                draws=args.posterior_draws,
                seed=90,
            ),
        ),
        (
            "posterior-0.95",
            lambda: posterior_confidence_rule(
                min_samples=args.min_samples,
                confidence=0.95,
                max_samples=args.max_samples,
                draws=args.posterior_draws,
                seed=95,
            ),
        ),
    ]
    metrics = [evaluate_trace_policy(name, rows, factory) for name, factory in policies]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(metrics[0]))
        writer.writeheader()
        writer.writerows(metrics)
    for row in metrics:
        print(
            f"{row['policy']:<14} accuracy={row['accuracy']:.3f} "
            f"mean_samples={row['mean_samples']:.2f} p90={row['p90_samples']:.1f} "
            f"mean_tokens={row['mean_tokens']:.1f}"
        )
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
