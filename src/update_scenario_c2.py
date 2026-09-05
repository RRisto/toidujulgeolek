#!/usr/bin/env python3
"""Propagate normalized 2025 EAT-Lancet demand into Scenario C2."""

from pathlib import Path

try:
    from update_scenario_c import update_scenario
except ImportError:  # imported as src.update_scenario_c2 in tests/tools
    from src.update_scenario_c import update_scenario


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    scenario_path = ROOT / "data/processed/scenario_comparison.csv"
    crosswalk_path = ROOT / "data/crosswalk/eatlancet2025_crosswalk.csv"
    rows = update_scenario(scenario_path, crosswalk_path, "C2")
    print(f"Updated Scenario C2 with normalized demand ({len(rows)} rows)")


if __name__ == "__main__":
    main()
