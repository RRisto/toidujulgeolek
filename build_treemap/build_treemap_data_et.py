#!/usr/bin/env python3
"""Build build_treemap/treemap_data_et.json — the Estonian counterpart of
treemap_data.json: same numbers, group/item names translated using the
existing dashboard_data_et.json (index-aligned with dashboard_data.json,
already reviewed/shipped Estonian translations), scenario labels translated
to match the wording already used in strings_et.json / strings_et_v2.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent

SCENARIO_LABELS_ET = {
    "A": "Praegune toitumine",
    "B": "TAI soovitatud toitumine",
    "C": "EAT-Lancet 2019",
    "C2": "EAT-Lancet 2025",
}

def build_et_data(root: Path) -> dict:
    """Return Estonian treemap data while preserving the UTF-8 wording."""
    d_en = json.loads(
        (root / "output/dashboard_data.json").read_text(encoding="utf-8")
    )["food_groups"]
    d_et = json.loads(
        (root / "output/dashboard_data_et.json").read_text(encoding="utf-8")
    )["food_groups"]
    assert len(d_en) == len(d_et), "EN/ET food_groups length mismatch"

    group_map = {}
    item_map = {}
    for en, et in zip(d_en, d_et):
        group_map[en["pyramid_group"]] = et["pyramid_group"]
        item_map[(en["pyramid_group"], en["subitem"])] = et["subitem"]

    data = json.loads(
        (root / "build_treemap/treemap_data.json").read_text(encoding="utf-8")
    )
    out = {"population": data["population"], "scenarios": []}
    for scn in data["scenarios"]:
        items = []
        for it in scn["items"]:
            et_group = group_map[it["group"]]
            et_subitem = item_map[(it["group"], it["item"])]
            et_label = et_group if et_subitem == "(kokku)" else et_subitem
            items.append({
                "group": et_group,
                "item": et_subitem,
                "g_per_day": it["g_per_day"],
                "pct": it["pct"],
                "label": et_label,
            })
        out["scenarios"].append({
            "key": scn["key"],
            "label": SCENARIO_LABELS_ET[scn["key"]],
            "total_g_per_day": scn["total_g_per_day"],
            "items": items,
        })
    return out


def main() -> None:
    out_path = ROOT / "build_treemap/treemap_data_et.json"
    out_path.write_text(
        json.dumps(build_et_data(ROOT), ensure_ascii=False, indent=0),
        encoding="utf-8",
    )
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
