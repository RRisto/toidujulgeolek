#!/usr/bin/env python3
"""Propagate normalized EAT-Lancet demand into the scenario comparison."""

from __future__ import annotations

import csv
from pathlib import Path


POPULATION = 1_339_785.0
ROOT = Path(__file__).resolve().parents[1]


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _load_crosswalk(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return {
            (row["pyramid_group"], row["subitem"]): float(
                row["scaled_normalized_g_per_day_estonia"]
            )
            for row in csv.DictReader(handle)
        }


def update_scenario(
    scenario_path: Path, crosswalk_path: Path, scenario: str
) -> list[dict[str, str]]:
    """Update Scenario C or C2 in-place using normalized edible-equivalent grams."""
    if scenario not in {"C", "C2"}:
        raise ValueError("scenario must be 'C' or 'C2'")

    crosswalk = _load_crosswalk(Path(crosswalk_path))
    with Path(scenario_path).open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    columns = [
        f"scenario_{scenario}_demand_tonnes_per_year",
        f"demand_change_ratio_{scenario}_over_A",
        f"scenario_{scenario}_self_sufficiency_pct",
    ]
    fieldnames = [name for name in fieldnames if name not in columns]
    for row in rows:
        for name in columns:
            row.pop(name, None)

    preceding = (
        "scenario_B_self_sufficiency_pct"
        if scenario == "C"
        else "scenario_C_self_sufficiency_pct"
    )
    insertion = fieldnames.index(preceding) + 1
    output_fields = fieldnames[:insertion] + columns + fieldnames[insertion:]

    for row in rows:
        key = (row["pyramid_group"], row["subitem"])
        normalized_g = crosswalk.get(key)
        demand = (
            round(normalized_g * POPULATION * 365 / 1_000_000, 1)
            if normalized_g is not None
            else None
        )
        a_demand = _to_float(row.get("scenario_A_demand_tonnes_per_year"))
        a_pct_text = row.get("scenario_A_self_sufficiency_pct", "")
        a_pct = _to_float(a_pct_text)

        row[columns[0]] = demand if demand is not None else ""
        ratio = round(demand / a_demand, 4) if demand and a_demand else None
        row[columns[1]] = ratio if ratio is not None else ""

        if a_pct is not None and demand and a_demand:
            row[columns[2]] = round(a_pct * a_demand / demand, 1)
        elif a_pct_text in {
            "~0% assumed",
            "~0% (raw sugar) / not scoreable (manufactured)",
        }:
            row[columns[2]] = a_pct_text
        elif "bimodal" in str(a_pct_text):
            row[columns[2]] = a_pct_text
        elif "upper bound" in str(a_pct_text) or "wide, unresolved" in str(
            a_pct_text
        ):
            row[columns[2]] = (
                "proportionally different from the Scenario A bound "
                f"(see {columns[1]}) -- not stated as a point estimate"
            )
        elif key in {
            ("Nuts, seeds, oils & fats", "Oils/fats/spreads (sunflower, 0%)"),
            ("Nuts, seeds, oils & fats", "Oils/fats/spreads (soy, 0%)"),
        }:
            row[columns[2]] = "0.0"
        else:
            row[columns[2]] = ""

        if scenario == "C2" and key == (
            "Sweets, snacks & discretionary",
            "(total)",
        ):
            prior = row.get("note", "").partition(" Phase 14:")[0]
            row["note"] = (
                prior
                + " Phase 21 correction: the 2025 EAT-Lancet added/free-sugar "
                "target is 30 g/day (115 kcal), not 6 g/day. Scenario C2 demand "
                "uses its energy-preserving TAI-basis normalized mass."
            )
        if key == ("Sweets, snacks & discretionary", "Honey"):
            row["note"] = (
                "PM29 reports 1,313 t production and 1,339 t human consumption "
                "in 2024. Honey remains a useful Scenario A/B self-sufficiency "
                "detail, but C/C2 demand is blank because EAT-Lancet sugar is "
                "already represented by the aggregate sweets row; adding Honey "
                "again would double-count diet mass."
            )

    with Path(scenario_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main() -> None:
    scenario_path = ROOT / "data/processed/scenario_comparison.csv"
    crosswalk_path = ROOT / "data/crosswalk/eatlancet_crosswalk.csv"
    rows = update_scenario(scenario_path, crosswalk_path, "C")
    print(f"Updated Scenario C with normalized demand ({len(rows)} rows)")


if __name__ == "__main__":
    main()
