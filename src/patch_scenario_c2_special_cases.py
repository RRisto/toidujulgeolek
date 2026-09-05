#!/usr/bin/env python3
"""Enforce structural Scenario C2 cases after the generic demand update.

Nuts/seeds remain 0% self-sufficient despite now having a known partial source
mass. Honey is deliberately blank: it is already represented in the aggregate
sweets/sugar row and must not be counted as an additional diet-mass leaf.
"""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    path = ROOT / "data/processed/scenario_comparison.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    for row in rows:
        key = (row["pyramid_group"], row["subitem"])
        if key == ("Nuts, seeds, oils & fats", "Nuts+Seeds,cocoa (combined)"):
            row["scenario_C2_self_sufficiency_pct"] = "0.0"
        if key == ("Sweets, snacks & discretionary", "Honey"):
            row["scenario_C2_demand_tonnes_per_year"] = ""
            row["demand_change_ratio_C2_over_A"] = ""
            row["scenario_C2_self_sufficiency_pct"] = ""

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print("Patched C2 nuts to structural 0%; excluded duplicate Honey demand")


if __name__ == "__main__":
    main()
