#!/usr/bin/env python3
"""Build the standalone Estonian EAT-Lancet 2025 sensitivity range chart."""

from __future__ import annotations

import csv
import math
from html import escape
from pathlib import Path


NUMERIC_FIELDS = (
    "baseline_g_per_day",
    "min_g_per_day",
    "max_g_per_day",
    "baseline_self_sufficiency_pct",
    "min_self_sufficiency_pct",
    "max_self_sufficiency_pct",
)

GROUP_LABELS = {
    "Vegetables, fruits & berries": "Köögiviljad, puuviljad ja marjad",
    "Grain products & potatoes": "Teraviljatooted ja kartul",
    "Dairy products": "Piimatooted",
    "Nuts, seeds, oils & fats": "Pähklid, seemned, õlid ja rasvad",
    "Fish, eggs & meat": "Kala, munad ja liha",
    "Sweets, snacks & discretionary": "Maiustused ja näksid",
}

ITEM_LABELS = {
    "Vegetables": "Köögiviljad",
    "Legumes": "Kaunviljad",
    "Fruits+Berries (combined)": "Puuviljad ja marjad",
    "High-fibre bread/baked goods": "Kiudainerikas leib ja pagaritooted",
    "Porridges/pasta/rice/grain products": "Pudrud, pasta, riis ja teraviljatooted",
    "Potato, sweet potato": "Kartul ja bataat",
    "Nuts+Seeds,cocoa (combined)": "Pähklid, seemned ja kakao",
    "Oils/fats/spreads (rapeseed, representative)": "Õlid, rasvad ja määrded",
    "Fish & seafood": "Kala ja mereannid",
    "Eggs": "Munad",
    "Poultry": "Linnuliha",
    "Red meat": "Punane liha",
}

GROUP_CLASSES = {
    "Vegetables, fruits & berries": "veg",
    "Grain products & potatoes": "grain",
    "Dairy products": "dairy",
    "Nuts, seeds, oils & fats": "nuts",
    "Fish, eggs & meat": "fish",
    "Sweets, snacks & discretionary": "sweets",
}


def load_rows(root: Path) -> list[dict[str, object]]:
    path = root / "data/processed/eatlancet2025_conversion_sensitivity.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for field in NUMERIC_FIELDS:
            row[field] = float(row[field]) if row[field] else None
    return rows


def _item_label(row: dict[str, object]) -> str:
    subitem = str(row["subitem"])
    if subitem == "(total)":
        return (
            "Piimatooted kokku"
            if row["pyramid_group"] == "Dairy products"
            else "Maiustused ja näksid kokku"
        )
    return ITEM_LABELS[subitem]


def _linear_position(value: float, maximum: float) -> float:
    return value / maximum * 100


def _log_position(value: float, maximum: float) -> float:
    return math.log10(1 + value) / math.log10(1 + maximum) * 100


def _fmt(value: float) -> str:
    return f"{value:.1f}"


def _range_plot(
    *,
    minimum: float | None,
    baseline: float | None,
    maximum: float | None,
    domain_max: float,
    scale,
    unit: str,
    color_class: str,
    accessible_label: str,
    open_ended: bool = False,
) -> str:
    if baseline is None or minimum is None:
        return (
            f'<div class="range-plot is-missing" role="img" '
            f'aria-label="{escape(accessible_label)}: määramata">'
            '<span class="missing-label">määramata</span></div>'
        )

    effective_maximum = domain_max if maximum is None else maximum
    left = scale(minimum, domain_max)
    right = scale(effective_maximum, domain_max)
    baseline_at = scale(baseline, domain_max)
    value_label = (
        f"{_fmt(minimum)}–nullnõudluse piir"
        if open_ended
        else f"{_fmt(minimum)}–{_fmt(maximum)}"
    )
    aria = (
        f"{accessible_label}: vahemik {value_label} {unit}, "
        f"lähtetase {_fmt(baseline)} {unit}"
    )
    open_class = " is-open" if open_ended else ""
    return (
        f'<div class="range-plot{open_class}" role="img" aria-label="{escape(aria)}">'
        f'<span class="range-line {color_class}" style="left:{left:.3f}%;width:{right-left:.3f}%"></span>'
        f'<span class="range-cap range-cap-min {color_class}" style="left:{left:.3f}%"></span>'
        + (
            f'<span class="range-arrow {color_class}" style="left:{right:.3f}%" aria-hidden="true">›</span>'
            if open_ended
            else f'<span class="range-cap range-cap-max {color_class}" style="left:{right:.3f}%"></span>'
        )
        + f'<span class="baseline-dot {color_class}" style="left:{baseline_at:.3f}%"></span>'
        f'<span class="range-value">{escape(value_label)}</span>'
        "</div>"
    )


def _axis(ticks: list[float], maximum: float, scale, unit: str) -> str:
    labels = "".join(
        f'<span class="axis-tick" style="left:{scale(value, maximum):.3f}%">'
        f'<i></i><b>{value:g}</b></span>'
        for value in ticks
    )
    return f'<div class="axis" aria-hidden="true">{labels}<span class="axis-unit">{unit}</span></div>'


def render_chart(root: Path) -> str:
    rows = load_rows(root)
    demand_max = 700.0
    self_sufficiency_max = 1000.0
    chart_rows: list[str] = []
    previous_group: str | None = None
    for row in rows:
        group = str(row["pyramid_group"])
        item = _item_label(row)
        group_label = GROUP_LABELS[group]
        color_class = GROUP_CLASSES[group]
        identity = f"{group_label}: {item}"
        demand = _range_plot(
            minimum=row["min_g_per_day"],
            baseline=row["baseline_g_per_day"],
            maximum=row["max_g_per_day"],
            domain_max=demand_max,
            scale=_linear_position,
            unit="g/päev",
            color_class=color_class,
            accessible_label=f"{identity}, päevane kogus",
        )
        self_sufficiency = _range_plot(
            minimum=row["min_self_sufficiency_pct"],
            baseline=row["baseline_self_sufficiency_pct"],
            maximum=row["max_self_sufficiency_pct"],
            domain_max=self_sufficiency_max,
            scale=_log_position,
            unit="%",
            color_class=color_class,
            accessible_label=f"{identity}, isevarustatus",
            open_ended=(
                row["baseline_self_sufficiency_pct"] is not None
                and row["max_self_sufficiency_pct"] is None
            ),
        )
        if group != previous_group:
            group_markup = f'<small class="group-name">{escape(group_label)}</small>'
            previous_group = group
        else:
            group_markup = '<small class="group-spacer" aria-hidden="true"></small>'
        chart_rows.append(
            '<div class="chart-row">'
            f'<div class="row-label">{group_markup}<strong>{escape(item)}</strong></div>'
            f'<div class="plot-cell" data-panel="Päevane kogus">{demand}</div>'
            f'<div class="plot-cell self-sufficiency" data-panel="Isevarustatus">{self_sufficiency}</div>'
            "</div>"
        )

    template = (root / "build_treemap/sensitivity_chart_template.html").read_text(
        encoding="utf-8"
    )
    replacements = {
        "__DEMAND_AXIS__": _axis(
            [0, 140, 280, 420, 560, 700], demand_max, _linear_position, "g/päev"
        ),
        "__SELF_SUFFICIENCY_AXIS__": _axis(
            [0, 10, 50, 100, 500, 1000],
            self_sufficiency_max,
            _log_position,
            "% (logaritmiline telg)",
        ),
        "__CHART_ROWS__": "".join(chart_rows),
        "__THRESHOLD_50__": f"{_log_position(50, self_sufficiency_max):.3f}",
        "__THRESHOLD_100__": f"{_log_position(100, self_sufficiency_max):.3f}",
    }
    for token, value in replacements.items():
        template = template.replace(token, value)
    unresolved = [token for token in replacements if token in template]
    if unresolved:
        raise ValueError(f"Unresolved chart placeholders: {unresolved}")
    return template


def build_chart(root: Path) -> Path:
    target = root / "output/eatlancet2025_sensitivity_et.html"
    target.write_text(render_chart(root), encoding="utf-8")
    return target


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    print(f"Wrote {build_chart(root)}")


if __name__ == "__main__":
    main()
