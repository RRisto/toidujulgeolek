#!/usr/bin/env python3
"""Build bilingual horizontal grouped bars comparing each food's diet share."""

from __future__ import annotations

import json
from pathlib import Path


LANGUAGE = {
    "en": {
        "data": "treemap_data.json",
        "output": "diet_bar_chart.html",
        "title": "Food share in each diet",
        "subtitle": "Each row compares the same food across four diets. Values are percentages of that diet's total daily mass.",
        "axis": "Share of diet mass (%)",
        "zero": "not represented",
        "total": "total",
        "unit": "g/day",
    },
    "et": {
        "data": "treemap_data_et.json",
        "output": "diet_bar_chart_et.html",
        "title": "Toidu osakaal igas dieedis",
        "subtitle": "Igal real võrreldakse sama toitu neljas dieedis. Väärtus näitab osakaalu selle dieedi päevasest kogumassist.",
        "axis": "Osakaal dieedi massist (%)",
        "zero": "ei ole esindatud",
        "total": "kokku",
        "unit": "g/päev",
    },
}


def build_comparison_matrix(root: Path, language: str = "en") -> dict:
    if language not in LANGUAGE:
        raise ValueError("language must be 'en' or 'et'")
    source = root / "build_treemap" / LANGUAGE[language]["data"]
    treemap = json.loads(source.read_text(encoding="utf-8"))
    scenario_keys = [scenario["key"] for scenario in treemap["scenarios"]]

    row_map = {}
    group_order = []
    for scenario in treemap["scenarios"]:
        for item in scenario["items"]:
            if item["item"] == "Honey":
                continue
            key = (item["group"], item["item"])
            if item["group"] not in group_order:
                group_order.append(item["group"])
            row = row_map.setdefault(
                key,
                {
                    "group": item["group"],
                    "item": item["item"],
                    "label": item["label"],
                    "percentages": {scenario_key: 0.0 for scenario_key in scenario_keys},
                    "grams": {scenario_key: 0.0 for scenario_key in scenario_keys},
                },
            )
            row["percentages"][scenario["key"]] = item["pct"]
            row["grams"][scenario["key"]] = item["g_per_day"]

    group_index = {group: index for index, group in enumerate(group_order)}
    rows = sorted(
        row_map.values(),
        key=lambda row: (
            group_index[row["group"]],
            -max(row["percentages"].values()),
            row["label"],
        ),
    )
    return {
        "population": treemap["population"],
        "scenarios": [
            {
                "key": scenario["key"],
                "label": scenario["label"],
                "total_g_per_day": scenario["total_g_per_day"],
            }
            for scenario in treemap["scenarios"]
        ],
        "rows": rows,
    }


def build_chart(root: Path, language: str) -> Path:
    copy = LANGUAGE[language]
    template = (root / "build_treemap/bar_chart_template.html").read_text(
        encoding="utf-8"
    )
    replacements = {
        "__LANG__": language,
        "__TITLE__": copy["title"],
        "__SUBTITLE__": copy["subtitle"],
        "__AXIS__": copy["axis"],
        "__ZERO__": copy["zero"],
        "__TOTAL__": copy["total"],
        "__UNIT__": copy["unit"],
        "__BAR_DATA__": json.dumps(
            build_comparison_matrix(root, language), ensure_ascii=False
        ),
    }
    for token, value in replacements.items():
        template = template.replace(token, value)
    unresolved = [token for token in replacements if token in template]
    if unresolved:
        raise ValueError(f"Unresolved chart placeholders: {unresolved}")
    target = root / "output" / copy["output"]
    target.write_text(template, encoding="utf-8")
    return target


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    for language in LANGUAGE:
        target = build_chart(root, language)
        print(f"Wrote {target}")


if __name__ == "__main__":
    main()
