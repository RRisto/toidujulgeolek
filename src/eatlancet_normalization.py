"""Normalize EAT-Lancet diets to the TAI edible/ready-to-eat mass basis.

EAT-Lancet source masses are retained for traceability.  Comparison masses are
derived from source energy and the representative grams-per-kcal implicit in
the Estonian TAI portion model, then energy-scaled to the Estonian reference
intake used by this project.
"""

from __future__ import annotations

import csv
import math
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path


ESTONIA_REFERENCE_KCAL = 2234.358
FoodKey = tuple[str, str]


@dataclass(frozen=True)
class SourceCategory:
    source_g: float
    source_kcal: float
    weight_basis: str


@dataclass(frozen=True)
class NormalizedRow:
    pyramid_group: str
    subitem: str
    source_g_per_day: float
    source_weight_basis: str
    source_kcal_per_day: float
    normalized_g_per_day_at_reference_kcal: float
    scaled_normalized_g_per_day_estonia: float
    normalization_method: str


EDITIONS = {
    "2019": {
        "reference_kcal": 2500.0,
        "categories": {
            "whole_grains": SourceCategory(232.0, 811.0, "dry"),
            "tubers": SourceCategory(50.0, 39.0, "edible_source_weight"),
            "vegetables": SourceCategory(300.0, 78.0, "edible_source_weight"),
            "fruit": SourceCategory(200.0, 126.0, "edible_source_weight"),
            "legumes": SourceCategory(75.0, 284.0, "dry"),
            "nuts": SourceCategory(50.0, 291.0, "edible_source_weight"),
            "dairy": SourceCategory(250.0, 153.0, "milk_equivalent"),
            "poultry": SourceCategory(29.0, 62.0, "edible_source_weight"),
            "fish": SourceCategory(28.0, 40.0, "edible_source_weight"),
            "eggs": SourceCategory(13.0, 19.0, "edible_source_weight"),
            "red_meat": SourceCategory(14.0, 30.0, "edible_source_weight"),
            "oils": SourceCategory(51.8, 450.0, "edible_source_weight"),
            "sugar": SourceCategory(31.0, 120.0, "edible_source_weight"),
        },
    },
    "2025": {
        "reference_kcal": 2400.0,
        "categories": {
            "whole_grains": SourceCategory(210.0, 735.0, "dry"),
            "tubers": SourceCategory(50.0, 50.0, "edible_source_weight"),
            "vegetables": SourceCategory(300.0, 95.0, "edible_source_weight"),
            "fruit": SourceCategory(200.0, 145.0, "edible_source_weight"),
            "legumes": SourceCategory(75.0, 275.0, "dry"),
            "nuts": SourceCategory(50.0, 275.0, "dry"),
            "dairy": SourceCategory(250.0, 145.0, "milk_equivalent"),
            "poultry": SourceCategory(30.0, 60.0, "edible_source_weight"),
            "fish": SourceCategory(30.0, 25.0, "edible_source_weight"),
            "eggs": SourceCategory(15.0, 20.0, "edible_source_weight"),
            "red_meat": SourceCategory(15.0, 45.0, "edible_source_weight"),
            "oils": SourceCategory(51.0, 455.0, "edible_source_weight"),
            "sugar": SourceCategory(30.0, 115.0, "edible_source_weight"),
        },
    },
}


DIRECT_DESTINATIONS = {
    "vegetables": ("Vegetables, fruits & berries", "Vegetables"),
    "legumes": ("Vegetables, fruits & berries", "Legumes"),
    "tubers": ("Grain products & potatoes", "Potato, sweet potato"),
    "dairy": ("Dairy products", "(total)"),
    "oils": (
        "Nuts, seeds, oils & fats",
        "Oils/fats/spreads (rapeseed, representative)",
    ),
    "fish": ("Fish, eggs & meat", "Fish & seafood"),
    "eggs": ("Fish, eggs & meat", "Eggs"),
    "poultry": ("Fish, eggs & meat", "Poultry"),
    "red_meat": ("Fish, eggs & meat", "Red meat"),
    "sugar": ("Sweets, snacks & discretionary", "(total)"),
}


def _read_lookup(path: Path, value_column: str) -> dict[tuple[str, str], float]:
    values: dict[tuple[str, str], set[float]] = {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            raw = row.get(value_column, "").strip()
            if raw:
                key = (row["pyramid_group"], row["subitem"])
                values.setdefault(key, set()).add(float(raw))
    ambiguous = {key: vals for key, vals in values.items() if len(vals) != 1}
    if ambiguous:
        raise ValueError(f"Expected one {value_column} per food row: {ambiguous}")
    return {key: next(iter(vals)) for key, vals in values.items()}


def _tai_density_inputs(root: Path):
    portions = _read_lookup(
        root / "data/crosswalk/portion_gram_representative.csv",
        "representative_g_per_portion",
    )
    calories = _read_lookup(
        root / "data/processed/tabelraamat_table13_portions.csv",
        "kcal_per_portion",
    )
    requirements = _read_lookup(
        root / "data/processed/requirement_model_national.csv",
        "avg_g_per_capita_per_day",
    )
    return portions, calories, requirements


def _density(
    keys: list[tuple[str, str]],
    portions: dict[tuple[str, str], float],
    calories: dict[tuple[str, str], float],
    requirements: dict[tuple[str, str], float],
) -> float:
    """Return representative TAI grams/kcal, preserving component mix."""
    total_g = sum(requirements[key] for key in keys)
    total_kcal = sum(
        requirements[key] / portions[key] * calories[key] for key in keys
    )
    return total_g / total_kcal


def build_crosswalk(
    edition: str,
    root: Path,
    *,
    density_overrides: Mapping[FoodKey, float] | None = None,
    whole_grain_bread_share: float | None = None,
) -> list[NormalizedRow]:
    if edition not in EDITIONS:
        raise ValueError(f"Unsupported EAT-Lancet edition: {edition}")

    config = EDITIONS[edition]
    categories: dict[str, SourceCategory] = config["categories"]
    reference_kcal = float(config["reference_kcal"])
    energy_scale = ESTONIA_REFERENCE_KCAL / reference_kcal
    portions, calories, requirements = _tai_density_inputs(root)
    overrides = dict(density_overrides or {})
    if (
        whole_grain_bread_share is not None
        and (
            not math.isfinite(whole_grain_bread_share)
            or not 0 <= whole_grain_bread_share <= 1
        )
    ):
        raise ValueError("whole_grain_bread_share must be between 0 and 1")

    densities: dict[tuple[str, str], float] = {
        key: portions[key] / calories[key] for key in portions
    }

    output: list[NormalizedRow] = []

    def add(
        destination: tuple[str, str],
        source: SourceCategory,
        density: float,
        method: str,
    ) -> None:
        normalized = source.source_kcal * density
        output.append(
            NormalizedRow(
                pyramid_group=destination[0],
                subitem=destination[1],
                source_g_per_day=source.source_g,
                source_weight_basis=source.weight_basis,
                source_kcal_per_day=source.source_kcal,
                normalized_g_per_day_at_reference_kcal=normalized,
                scaled_normalized_g_per_day_estonia=normalized * energy_scale,
                normalization_method=method,
            )
        )

    def selected_density(destination: FoodKey, baseline: float) -> float:
        value = overrides.get(destination, baseline)
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"Density must be positive for {destination}: {value}")
        return value

    grain = categories["whole_grains"]
    bread_key = ("Grain products & potatoes", "High-fibre bread/baked goods")
    porridge_key = (
        "Grain products & potatoes",
        "Porridges/pasta/rice/grain products",
    )
    bread_tai_kcal = requirements[bread_key] / portions[bread_key] * calories[bread_key]
    porridge_tai_kcal = (
        requirements[porridge_key] / portions[porridge_key] * calories[porridge_key]
    )
    bread_share = bread_tai_kcal / (bread_tai_kcal + porridge_tai_kcal)
    if whole_grain_bread_share is not None:
        bread_share = whole_grain_bread_share
    for key, share in ((bread_key, bread_share), (porridge_key, 1 - bread_share)):
        add(
            key,
            SourceCategory(
                grain.source_g * share,
                grain.source_kcal * share,
                grain.weight_basis,
            ),
            selected_density(key, densities[key]),
            "Source whole-grain mass and energy split by TAI bread/porridge "
            "energy shares; converted using the destination TAI g/kcal.",
        )

    for category, destination in DIRECT_DESTINATIONS.items():
        lookup_key = destination
        if category == "oils":
            lookup_key = ("Nuts, seeds, oils & fats", "Oils/fats/spreads")
        add(
            destination,
            categories[category],
            selected_density(destination, densities[lookup_key]),
            "Source energy converted using the destination TAI representative g/kcal.",
        )

    fruit_keys = [
        ("Vegetables, fruits & berries", "Fruits"),
        ("Vegetables, fruits & berries", "Berries"),
    ]
    add(
        ("Vegetables, fruits & berries", "Fruits+Berries (combined)"),
        categories["fruit"],
        selected_density(
            ("Vegetables, fruits & berries", "Fruits+Berries (combined)"),
            _density(fruit_keys, portions, calories, requirements),
        ),
        "Source fruit energy converted using the TAI fruit/berry component mix.",
    )

    nut_keys = [
        ("Nuts, seeds, oils & fats", "Nuts"),
        ("Nuts, seeds, oils & fats", "Seeds, cocoa"),
    ]
    add(
        ("Nuts, seeds, oils & fats", "Nuts+Seeds,cocoa (combined)"),
        categories["nuts"],
        selected_density(
            ("Nuts, seeds, oils & fats", "Nuts+Seeds,cocoa (combined)"),
            _density(nut_keys, portions, calories, requirements),
        ),
        "Source nut energy converted using the TAI nuts/seeds component mix.",
    )

    order = {
        key: index
        for index, key in enumerate(
            [
                ("Vegetables, fruits & berries", "Vegetables"),
                ("Vegetables, fruits & berries", "Legumes"),
                ("Vegetables, fruits & berries", "Fruits+Berries (combined)"),
                bread_key,
                porridge_key,
                ("Grain products & potatoes", "Potato, sweet potato"),
                ("Dairy products", "(total)"),
                ("Nuts, seeds, oils & fats", "Nuts+Seeds,cocoa (combined)"),
                DIRECT_DESTINATIONS["oils"],
                ("Fish, eggs & meat", "Fish & seafood"),
                ("Fish, eggs & meat", "Eggs"),
                ("Fish, eggs & meat", "Poultry"),
                ("Fish, eggs & meat", "Red meat"),
                ("Sweets, snacks & discretionary", "(total)"),
            ]
        )
    }
    unknown = set(overrides) - {
        (row.pyramid_group, row.subitem) for row in output
    }
    if unknown:
        raise ValueError(
            f"Unknown density override destinations: {sorted(unknown)}"
        )
    return sorted(output, key=lambda row: order[(row.pyramid_group, row.subitem)])


def write_crosswalk(edition: str, root: Path) -> Path:
    filename = (
        "eatlancet_crosswalk.csv"
        if edition == "2019"
        else "eatlancet2025_crosswalk.csv"
    )
    target = root / "data/crosswalk" / filename
    rows = build_crosswalk(edition, root)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(asdict(rows[0])), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)
    return target


def main(edition: str) -> None:
    root = Path(__file__).resolve().parents[1]
    target = write_crosswalk(edition, root)
    print(f"Wrote {target}")
