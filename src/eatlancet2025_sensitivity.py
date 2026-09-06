"""Candidate conversions for EAT-Lancet 2025 sensitivity analysis."""

from __future__ import annotations

import csv
import math
from dataclasses import asdict, dataclass
from pathlib import Path

from src.eatlancet_normalization import FoodKey, NormalizedRow, build_crosswalk


POPULATION = 1_339_785
TONNES_FACTOR = POPULATION * 365 / 1_000_000


@dataclass(frozen=True)
class SensitivityResult:
    pyramid_group: str
    subitem: str
    baseline_g_per_day: float
    min_g_per_day: float
    max_g_per_day: float
    baseline_demand_tonnes: float
    min_demand_tonnes: float
    max_demand_tonnes: float
    baseline_self_sufficiency_pct: float | None
    min_self_sufficiency_pct: float | None
    max_self_sufficiency_pct: float | None
    max_abs_change_g_per_day: float
    max_relative_change_pct: float
    min_variant: str
    max_variant: str
    crosses_50pct: bool | None
    crosses_100pct: bool | None
    method_note: str


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
    baseline_rows = {
        (row.pyramid_group, row.subitem): row
        for row in build_crosswalk("2025", root)
    }
    expected = set(baseline_rows)
    table16: dict[str, list[dict[str, str]]] = {}
    source_path = root / "data/raw/tai/tabelraamat_table16_portion_grams.csv"
    with source_path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            table16.setdefault(row["item_et"], []).append(row)
    grain_keys = {
        ("Grain products & potatoes", "High-fibre bread/baked goods"),
        ("Grain products & potatoes", "Porridges/pasta/rice/grain products"),
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
            kind = source["source_kind"]
            if kind not in {"baseline", "tai_table16", "grain_allocation"}:
                raise ValueError(f"Invalid sensitivity source kind: {identity}: {kind}")

            portion = float(source["portion_g"]) if source["portion_g"] else None
            kcal = (
                float(source["kcal_per_portion"])
                if source["kcal_per_portion"]
                else None
            )
            if (portion is None) != (kcal is None):
                raise ValueError(f"Incomplete portion energy pair: {identity}")
            if portion is not None and (
                not math.isfinite(portion) or not math.isfinite(kcal)
                or portion <= 0 or kcal <= 0
            ):
                raise ValueError(f"Non-finite or non-positive portion energy pair: {identity}")

            share = (
                float(source["whole_grain_bread_share"])
                if source["whole_grain_bread_share"]
                else None
            )
            if kind == "grain_allocation":
                if portion is not None or share not in {0.0, 1.0} or destination not in grain_keys:
                    raise ValueError(f"Invalid grain allocation: {identity}")
            else:
                if share is not None:
                    raise ValueError(f"Allocation is exclusive to grain-allocation rows: {identity}")
                if kind == "tai_table16":
                    if portion is None:
                        raise ValueError(f"Missing TAI portion energy pair: {identity}")
                    matches = table16.get(source["source_label"], [])
                    if len(matches) != 1:
                        raise ValueError(f"Missing or ambiguous Table 16 source: {identity}")
                    published = matches[0]
                    allowed_portions = {
                        float(published[field])
                        for field in ("portion_g", "portion_g_range_low", "portion_g_range_high")
                        if published[field]
                    }
                    if portion not in allowed_portions or kcal != float(published["kcal_per_portion"]):
                        raise ValueError(f"Unsupported Table 16 portion energy pair: {identity}")
                elif portion is not None:
                    baseline = baseline_rows[destination]
                    # Compare the original forward calculation exactly: dividing
                    # normalized grams back into a density adds rounding noise.
                    if baseline.source_kcal_per_day * (portion / kcal) != baseline.normalized_g_per_day_at_reference_kcal:
                        raise ValueError(f"Baseline pair changes the default conversion: {identity}")

            result[destination].append(
                ConversionVariant(
                    destination=destination,
                    name=source["variant_name"],
                    grams_per_kcal=(portion / kcal if portion is not None else None),
                    whole_grain_bread_share=share,
                    source_kind=kind,
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


def _parse_point_estimate(value: str) -> float | None:
    """Accept only a complete, finite numeric point estimate."""
    text = value.strip()
    if not text:
        return None
    try:
        parsed = float(text)
    except ValueError:
        return None
    return parsed if math.isfinite(parsed) else None


def _load_scenario_c2(root: Path) -> dict[FoodKey, tuple[float, float | None]]:
    path = root / "data/processed/scenario_comparison.csv"
    result: dict[FoodKey, tuple[float, float | None]] = {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row["pyramid_group"], row["subitem"])
            raw_demand = row["scenario_C2_demand_tonnes_per_year"].strip()
            if not raw_demand:
                continue
            demand = float(raw_demand)
            if key in result:
                raise ValueError(f"Duplicate Scenario C.2 row: {key}")
            result[key] = (
                demand,
                _parse_point_estimate(row["scenario_C2_self_sufficiency_pct"]),
            )
    return result


def _crosses(low: float | None, high: float | None, threshold: float) -> bool | None:
    if low is None or high is None:
        return None
    return low < threshold <= high


def _crosses_with_zero_demand_limit(
    low: float | None,
    high: float | None,
    minimum_demand: float,
    baseline_self_sufficiency: float | None,
    baseline_demand: float,
    threshold: float,
) -> bool | None:
    """Preserve threshold information when a zero-demand endpoint is undefined."""
    if minimum_demand != 0:
        return _crosses(low, high, threshold)
    if baseline_self_sufficiency is None:
        return None
    production = baseline_self_sufficiency * baseline_demand
    if production <= 0 or low is None:
        return False
    return low < threshold


def _extreme(observations: list[tuple[str, float]], *, highest: bool) -> tuple[str, float]:
    values = [value for _, value in observations]
    target = max(values) if highest else min(values)
    if math.isclose(observations[0][1], target, rel_tol=1e-12, abs_tol=1e-12):
        return observations[0]
    return next(
        observation
        for observation in observations
        if math.isclose(observation[1], target, rel_tol=1e-12, abs_tol=1e-12)
    )


def analyze(root: Path) -> list[SensitivityResult]:
    """Calculate conversion-driven ranges around Scenario C.2 demand."""
    baseline_rows = build_crosswalk("2025", root)
    baseline_by_key = {
        (row.pyramid_group, row.subitem): row for row in baseline_rows
    }
    scenario_c2 = _load_scenario_c2(root)
    missing = set(baseline_by_key) - set(scenario_c2)
    if missing:
        raise ValueError(f"Missing Scenario C.2 rows: {sorted(missing)}")

    observations: dict[FoodKey, list[tuple[str, float]]] = {
        key: [("baseline", row.scaled_normalized_g_per_day_estonia)]
        for key, row in baseline_by_key.items()
    }
    grain_keys = {
        ("Grain products & potatoes", "High-fibre bread/baked goods"),
        ("Grain products & potatoes", "Porridges/pasta/rice/grain products"),
    }
    for destination, variants in load_candidates(root).items():
        for variant in variants:
            recomputed = {
                (row.pyramid_group, row.subitem): row.scaled_normalized_g_per_day_estonia
                for row in variant_crosswalk(root, variant)
            }
            affected = grain_keys if variant.source_kind == "grain_allocation" else {destination}
            for key in affected:
                observations[key].append((variant.name, recomputed[key]))

    results: list[SensitivityResult] = []
    for baseline in baseline_rows:
        key = (baseline.pyramid_group, baseline.subitem)
        min_variant, min_g = _extreme(observations[key], highest=False)
        max_variant, max_g = _extreme(observations[key], highest=True)
        baseline_demand, baseline_self_sufficiency = scenario_c2[key]
        baseline_g = baseline.scaled_normalized_g_per_day_estonia
        min_demand = (
            baseline_demand
            if min_g == baseline_g
            else baseline_demand * min_g / baseline_g
        )
        max_demand = (
            baseline_demand
            if max_g == baseline_g
            else baseline_demand * max_g / baseline_g
        )
        min_self_sufficiency = (
            baseline_self_sufficiency * baseline_demand / max_demand
            if baseline_self_sufficiency is not None
            else None
        )
        max_self_sufficiency = (
            baseline_self_sufficiency * baseline_demand / min_demand
            if min_demand and baseline_self_sufficiency is not None
            else None
        )
        max_abs_change = max(abs(min_g - baseline_g), abs(max_g - baseline_g))
        results.append(
            SensitivityResult(
                pyramid_group=baseline.pyramid_group,
                subitem=baseline.subitem,
                baseline_g_per_day=baseline_g,
                min_g_per_day=min_g,
                max_g_per_day=max_g,
                baseline_demand_tonnes=baseline_demand,
                min_demand_tonnes=min_demand,
                max_demand_tonnes=max_demand,
                baseline_self_sufficiency_pct=baseline_self_sufficiency,
                min_self_sufficiency_pct=min_self_sufficiency,
                max_self_sufficiency_pct=max_self_sufficiency,
                max_abs_change_g_per_day=max_abs_change,
                max_relative_change_pct=100 * max_abs_change / baseline_g,
                min_variant=min_variant,
                max_variant=max_variant,
                crosses_50pct=_crosses_with_zero_demand_limit(
                    min_self_sufficiency,
                    max_self_sufficiency,
                    min_demand,
                    baseline_self_sufficiency,
                    baseline_demand,
                    50,
                ),
                crosses_100pct=_crosses_with_zero_demand_limit(
                    min_self_sufficiency,
                    max_self_sufficiency,
                    min_demand,
                    baseline_self_sufficiency,
                    baseline_demand,
                    100,
                ),
                method_note=(
                    "Scenario C.2 demand is ratio-scaled from the checked-in "
                    "baseline; conversion variants recompute the 2025 crosswalk."
                ),
            )
        )
    return results


def _format_csv_value(name: str, value: object) -> object:
    if value is None:
        return ""
    if name in {"max_abs_change_g_per_day", "max_relative_change_pct"}:
        return f"{value:.1f}"
    if name.endswith("_g_per_day"):
        return f"{value:.3f}"
    if "demand_tonnes" in name or "self_sufficiency_pct" in name:
        return f"{value:.1f}"
    return value


def write_csv(root: Path, rows: list[SensitivityResult]) -> Path:
    """Write deterministically rounded sensitivity results."""
    target = root / "data/processed/eatlancet2025_conversion_sensitivity.csv"
    fieldnames = list(SensitivityResult.__dataclass_fields__)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for result in rows:
            writer.writerow(
                {
                    name: _format_csv_value(name, value)
                    for name, value in asdict(result).items()
                }
            )
    return target


def _format_range(low: float, high: float, unit: str) -> str:
    """Format a reported interval with a single, consistent precision."""
    return f"{low:.1f}–{high:.1f} {unit}"


def _format_self_sufficiency(
    low: float | None, high: float | None, baseline: float | None
) -> str:
    """Show a finite endpoint even when zero demand makes the other undefined."""
    if low is None and high is None:
        return "isevarustuskindluse punktihinnang puudub"
    if low is None:
        return (
            "määramata nullnõudluse piir–"
            f"{high:.1f}% (lähtetase {baseline:.1f}%)"
        )
    if high is None:
        return (
            f"{low:.1f}%–määramata nullnõudluse piir "
            f"(lähtetase {baseline:.1f}%)"
        )
    return _format_range(low, high, "%")


def _row_identity(row: SensitivityResult) -> str:
    """Return the unambiguous report label for a sensitivity row."""
    return f"{row.pyramid_group} — {row.subitem}"


def render_report(rows: list[SensitivityResult]) -> str:
    """Render the Estonian findings report solely from sensitivity results."""
    largest = sorted(
        rows, key=lambda row: row.max_relative_change_pct, reverse=True
    )[:5]
    crossings = [
        row for row in rows if row.crosses_50pct or row.crosses_100pct
    ]
    unchanged = [
        row for row in rows if row.min_g_per_day == row.max_g_per_day
    ]
    movements = []
    for row in rows:
        baseline = row.baseline_self_sufficiency_pct
        if baseline is None or not math.isfinite(baseline):
            continue
        changes = [
            abs(endpoint - baseline)
            for endpoint in (row.min_self_sufficiency_pct, row.max_self_sufficiency_pct)
            if endpoint is not None and math.isfinite(endpoint)
        ]
        if changes and max(changes) > 0:
            movements.append((max(changes), row))
    movements.sort(key=lambda item: item[0], reverse=True)

    lines = [
        "# EAT–Lancet 2025 → TAI teisenduse tundlikkus",
        "",
        "## Mida testiti",
        "",
        "Analüüs on dokumenteeritud TAI esindusportsjonite ja täistera "
        "leiva-pudru jaotuse ühekaupa muutmise deterministlik "
        "tundlikkusvahemik. Iga vahemik sisaldab lähtetaset ning saadakse "
        "tundlikkusarvutuse tulemusobjektidest.",
        "",
        "## Suurima mõjuga toidugrupid",
        "",
        "Viis suurimat suhtelist liikumist teisendatud koguses:",
        "",
    ]
    for row in largest:
        lines.append(
            f"- **{_row_identity(row)}**: {_format_range(row.min_g_per_day, row.max_g_per_day, 'g/päev')} "
            f"(lähtetase {row.baseline_g_per_day:.1f} g/päev; suurim muutus "
            f"{row.max_relative_change_pct:.1f}%). Nõudlus: "
            f"{_format_range(row.min_demand_tonnes, row.max_demand_tonnes, 't/a')}; "
            f"isevarustuskindlus: {_format_self_sufficiency(row.min_self_sufficiency_pct, row.max_self_sufficiency_pct, row.baseline_self_sufficiency_pct)}."
        )

    lines.extend([
        "", "## Suurimad isevarustuskindluse muutused", "",
        "Kuni viis suurimat lõplikku absoluutset muutust lähtetasemest "
        "protsendipunktides. Nullnõudluse määramata otspunkti ei järjestata; "
        "sama rea lõplik otspunkt jääb võrdlusse.", "",
    ])
    for change, row in movements[:5]:
        lines.append(
            f"- **{_row_identity(row)}**: "
            f"{_format_self_sufficiency(row.min_self_sufficiency_pct, row.max_self_sufficiency_pct, row.baseline_self_sufficiency_pct)} "
            f"(lähtetase {row.baseline_self_sufficiency_pct:.1f}%; "
            f"suurim lõplik muutus {change:.1f} protsendipunkti)."
        )
    if not movements:
        lines.append("- Lõplikud isevarustuskindluse muutused puuduvad.")

    lines.extend(["", "## Lävendite ületamised", ""])
    if crossings:
        for row in crossings:
            thresholds = []
            if row.crosses_50pct:
                thresholds.append("50%")
            if row.crosses_100pct:
                thresholds.append("100%")
            lines.append(
                f"- **{_row_identity(row)}** ületab vahemikus "
                f"{_format_self_sufficiency(row.min_self_sufficiency_pct, row.max_self_sufficiency_pct, row.baseline_self_sufficiency_pct)} "
                f"lävendi/lävendid {', '.join(thresholds)}."
            )
    else:
        lines.append("- Ükski rida ei ületa testitud vahemikus 50% ega 100% lävendit.")

    lines.extend(["", "## Millised järeldused püsivad", ""])
    stable: dict[str, list[str]] = {"üle 100%": [], "alla 50%": [], "50–100%": []}
    unresolved = []
    zero_demand = []
    for row in rows:
        if row.baseline_self_sufficiency_pct is None:
            unresolved.append(f"**{_row_identity(row)}**")
            continue
        if row.min_demand_tonnes == 0:
            zero_demand.append(
                f"**{_row_identity(row)}** "
                f"({_format_self_sufficiency(row.min_self_sufficiency_pct, row.max_self_sufficiency_pct, row.baseline_self_sufficiency_pct)})"
            )
            continue
        low, high = row.min_self_sufficiency_pct, row.max_self_sufficiency_pct
        if low is None or high is None or not all(map(math.isfinite, (low, high))):
            continue
        category = (
            "üle 100%" if low > 100 else
            "alla 50%" if high < 50 else
            "50–100%" if low >= 50 and high <= 100 else None
        )
        if category is not None:
            stable[category].append(
                f"**{_row_identity(row)}** ({_format_range(low, high, '%')})"
            )
    for category, names in stable.items():
        if names:
            lines.append(f"- Kõigis testitud variantides püsivad {category}: {', '.join(names)}.")
    if unresolved:
        lines.append(f"- Isevarustuskindluse punktihinnang puudub: {', '.join(unresolved)}.")
    if zero_demand:
        lines.append(
            f"- Määramata nullnõudluse piir: {', '.join(zero_demand)}. "
            "Neile ei omistata kõiki variante hõlmavat lõplikku klassifikatsiooni."
        )
    if unchanged:
        names = ", ".join(f"**{_row_identity(row)}**" for row in unchanged)
        lines.append(
            f"- Muutumatute eeldustega read on {names}; nende min- ja max-kogus on sama."
        )
    lines.extend(
        [
            "- Kõigi ridade vahemikud on tingitud ainult teisendusvalikutest; "
            "tootmist ja kaubanduskäitumist ei muudetud.",
            "- EAT-Lancet'i energia ja rahvastiku energiavajadust ei muudetud; "
            "seega ei kirjelda tulemused nende eelduste mõju.",
            "",
            "## Tõlgendamise piirid",
            "",
            "See deterministlik tundlikkusvahemik ei ole usaldusvahemik ega "
            "tõenäosusjaotus. See ei anna tõenäosust ühelegi tulemusele ja ei kata "
            "EAT-Lancet'i sihtide, energiavajaduse, tootmise, kadude ega "
            "kaubanduskäitumise ebakindlust.",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(root: Path, rows: list[SensitivityResult]) -> Path:
    """Write the deterministic Estonian report next to project documentation."""
    target = root / "docs/eatlancet2025_conversion_sensitivity_et.md"
    target.write_text(render_report(rows), encoding="utf-8", newline="\n")
    return target


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    rows = analyze(root)
    csv_target = write_csv(root, rows)
    report_target = write_report(root, rows)
    print(f"Wrote {csv_target}")
    print(f"Wrote {report_target}")


if __name__ == "__main__":
    main()
