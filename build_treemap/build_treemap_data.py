#!/usr/bin/env python3
"""Build deterministic treemap data from canonical dashboard demand values."""

from __future__ import annotations

import json
from pathlib import Path


POPULATION = 1_339_785
SCENARIO_LABELS = {
    "A": "Current diet",
    "B": "TAI-recommended diet",
    "C": "EAT-Lancet 2019",
    "C2": "EAT-Lancet 2025",
}


def build_treemap_data(root: Path) -> dict:
    dashboard = json.loads(
        (root / "output/dashboard_data.json").read_text(encoding="utf-8")
    )
    scenarios = []
    for key, label in SCENARIO_LABELS.items():
        items = []
        demand_field = f"demand_{key}_tonnes"
        for row in dashboard["food_groups"]:
            tonnes = row.get(demand_field)
            if not tonnes or row["subitem"] == "Honey":
                continue
            grams = round(float(tonnes) * 1_000_000 / (POPULATION * 365), 1)
            if grams <= 0:
                continue
            items.append(
                {
                    "group": row["pyramid_group"],
                    "item": row["subitem"],
                    "g_per_day": grams,
                    "label": (
                        row["pyramid_group"]
                        if row["subitem"] == "(total)"
                        else row["subitem"]
                    ),
                }
            )
        items.sort(key=lambda item: (-item["g_per_day"], item["group"], item["item"]))
        total = round(sum(item["g_per_day"] for item in items), 1)
        for item in items:
            item["pct"] = round(item["g_per_day"] / total * 100, 1)
        scenarios.append(
            {
                "key": key,
                "label": label,
                "total_g_per_day": total,
                "items": items,
            }
        )
    return {"population": POPULATION, "scenarios": scenarios}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    target = root / "build_treemap/treemap_data.json"
    target.write_text(
        json.dumps(build_treemap_data(root), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {target}")


if __name__ == "__main__":
    main()
