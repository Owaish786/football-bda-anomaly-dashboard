"""CLI entry point for the Football BDA evaluation pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from backend.services.evaluation_service import run_evaluation


def main() -> int:
    report = run_evaluation()
    report_path = Path("data") / "model_evaluation.json"

    print("Football BDA evaluation report")
    print("=" * 40)
    print(f"Report saved to: {report_path}")
    print(f"Matches evaluated: {report['dataset']['matches']}")
    print(f"Features used: {report['dataset']['features']}")
    print("\nClassification metrics:")
    print(json.dumps(report["classification"]["metrics"], indent=2))
    print("\nRegression metrics:")
    print(json.dumps(report["regression"]["metrics"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())