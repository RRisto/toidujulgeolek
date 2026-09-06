"""Candidate conversions for EAT-Lancet 2025 sensitivity analysis."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from src.eatlancet_normalization import FoodKey, NormalizedRow, build_crosswalk


@dataclass(frozen=True)
class ConversionVariant:
    destination: FoodKey
    name: str
    grams_per_kcal: float | None
    whole_grain_bread_share: float | None
    source_kind: str
    source_label: str


def load_candidates(root: Path) -> dict[FoodKey, list[ConversionVariant]]:
    """Load validated, traceable conversion candidates grouped by destination."""
    path = root / "data/crosswalk/eatlancet2025_sensitivity_candidates.csv"
    expected = {
        (row.pyramid_group, row.subitem)
        for row in build_crosswalk("2025", root)
    }
    result: dict[FoodKey, list[ConversionVariant]] = {key: [] for key in expected}
    seen: set[tuple[FoodKey, str]] = set()

    with path.open(encoding="utf-8-sig", newline="") as handle:
        for source in csv.DictReader(handle):
            destination = (source["pyramid_group"], source["subitem"])
            if destination not in expected:
                raise ValueError(f"Unknown sensitivity destination: {destination}")
            identity = (destination, source["variant_name"])
            if identity in seen:
                raise ValueError(f"Duplicate sensitivity variant: {identity}")
            seen.add(identity)

            portion = float(source["portion_g"]) if source["portion_g"] else None
            kcal = (
                float(source["kcal_per_portion"])
                if source["kcal_per_portion"]
                else None
            )
            if (portion is None) != (kcal is None):
                raise ValueError(f"Incomplete portion energy pair: {identity}")
            if portion is not None and (portion <= 0 or kcal <= 0):
                raise ValueError(f"Non-positive portion energy pair: {identity}")

            share = (
                float(source["whole_grain_bread_share"])
                if source["whole_grain_bread_share"]
                else None
            )
            if share is not None and not 0 <= share <= 1:
                raise ValueError(f"Invalid grain allocation: {identity}")

            result[destination].append(
                ConversionVariant(
                    destination=destination,
                    name=source["variant_name"],
                    grams_per_kcal=(portion / kcal if portion is not None else None),
                    whole_grain_bread_share=share,
                    source_kind=source["source_kind"],
                    source_label=source["source_label"],
                )
            )

    missing = [key for key, variants in result.items() if not variants]
    if missing:
        raise ValueError(f"Destinations without sensitivity candidates: {missing}")
    return result


def variant_crosswalk(root: Path, variant: ConversionVariant) -> list[NormalizedRow]:
    """Recompute the complete 2025 crosswalk for one candidate variant."""
    densities = (
        {variant.destination: variant.grams_per_kcal}
        if variant.grams_per_kcal is not None
        else {}
    )
    return build_crosswalk(
        "2025",
        root,
        density_overrides=densities,
        whole_grain_bread_share=variant.whole_grain_bread_share,
    )
