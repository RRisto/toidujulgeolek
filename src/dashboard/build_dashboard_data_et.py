#!/usr/bin/env python3
"""Refresh Estonian dashboard numbers while preserving reviewed translations."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NUMBER = re.compile(r"^-?\d+(?:\.\d+)?%?$")


def _sync(en, et, key=""):
    if isinstance(en, dict):
        prior = et if isinstance(et, dict) else {}
        return {name: _sync(value, prior.get(name), name) for name, value in en.items()}
    if isinstance(en, list):
        prior = et if isinstance(et, list) else []
        return [
            _sync(value, prior[index] if index < len(prior) else None, key)
            for index, value in enumerate(en)
        ]
    if isinstance(en, str):
        if not en or NUMBER.fullmatch(en):
            return en
        return et if isinstance(et, str) and et else en
    return en


def build(root: Path = ROOT) -> dict:
    en = json.loads((root / "output/dashboard_data.json").read_text(encoding="utf-8"))
    et_path = root / "output/dashboard_data_et.json"
    et = json.loads(et_path.read_text(encoding="utf-8"))
    output = _sync(en, et)

    for en_row, et_row in zip(en["food_groups"], output["food_groups"], strict=True):
        key = (en_row["pyramid_group"], en_row["subitem"])
        if key == ("Sweets, snacks & discretionary", "(total)"):
            et_row["note"] = (
                "21. etapi parandus: EAT-Lancet 2025 lisatud/vabade suhkrute "
                "siht on 30 g päevas (115 kcal), mitte 6 g. C2 nõudlus kasutab "
                "energia säilitavat TAI-massialuse teisendust."
            )
        if key == ("Sweets, snacks & discretionary", "Honey"):
            et_row["note"] = (
                "Mee A/B detail säilib, kuid C/C2 nõudlus jäetakse tühjaks: "
                "EAT-Lanceti suhkur on juba maiustuste koondreas ning mee eraldi "
                "lisamine loendaks sama massi kaks korda."
            )
            et_row["flag_reason"] = (
                "Mee A/B detail säilib; C/C2 ei hinnata, sest mesi sisaldub "
                "juba maiustuste/suhkru koondmassis."
            )
    return output


def main() -> None:
    target = ROOT / "output/dashboard_data_et.json"
    target.write_text(
        json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {target}")


if __name__ == "__main__":
    main()
