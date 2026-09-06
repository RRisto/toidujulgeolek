# EAT-Lancet 2025 Conversion Sensitivity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone, auditable sensitivity analysis showing how documented alternative TAI representative compositions change EAT-Lancet 2025 demand and self-sufficiency by food-group subitem.

**Architecture:** Add optional conversion overrides to the existing normalization boundary while preserving its default output. A separate EAT-Lancet 2025 analysis module will load a curated, source-labelled candidate catalog, run one-at-a-time variants, aggregate row-level extrema, and generate a CSV plus an Estonian Markdown report without touching Scenario C.2 or dashboard artifacts.

**Tech Stack:** Python 3 standard library (`csv`, `dataclasses`, `pathlib`, `unittest`); existing CSV model outputs; Markdown.

**Spec:** `docs/superpowers/specs/2026-09-06-eatlancet-2025-conversion-sensitivity-design.md`

## Global Constraints

- Analyze EAT-Lancet 2025 only.
- Hold EAT source energy, Estonia's 2,234.358 kcal reference, population, production, Scenario A inputs, taxonomy, and direct mappings constant.
- Vary only TAI representative grams-per-kcal and the whole-grain bread share.
- Candidate values must be traceable to TAI Table 16 or to the explicit 0%/100% grain-allocation endpoints; do not use arbitrary percentage shocks.
- Use deterministic one-at-a-time variants; do not call the result a confidence interval or probability distribution.
- Do not modify Scenario C.2, dashboard data, dashboard generators, or published HTML.
- Preserve all unrelated working-tree changes and stage only files named by the current task.

## File Structure

- Modify `src/eatlancet_normalization.py`: accept optional density and whole-grain-allocation overrides while leaving the default crosswalk unchanged.
- Modify `data/raw/tai/tabelraamat_table16_portion_grams.csv`: add the four already-documented dairy subtype rows missing from the structured extract so every dairy sensitivity candidate has a machine-readable TAI source row.
- Create `data/crosswalk/eatlancet2025_sensitivity_candidates.csv`: curated mapping from each C.2 destination to allowed TAI Table 16 candidates.
- Create `src/eatlancet2025_sensitivity.py`: load candidates, execute variants, aggregate ranges, and write outputs.
- Create `tests/test_eatlancet2025_sensitivity.py`: regression, provenance, calculation, range, and output tests.
- Create `data/processed/eatlancet2025_conversion_sensitivity.csv`: generated row-level results.
- Create `docs/eatlancet2025_conversion_sensitivity_et.md`: generated Estonian findings.

---

### Task 1: Add an explicit normalization override seam

**Files:**
- Modify: `src/eatlancet_normalization.py`
- Modify: `tests/test_eatlancet_normalization.py`

**Interfaces:**
- Consumes: existing `build_crosswalk(edition: str, root: Path)` behavior.
- Produces: `build_crosswalk(edition: str, root: Path, *, density_overrides: Mapping[tuple[str, str], float] | None = None, whole_grain_bread_share: float | None = None) -> list[NormalizedRow]`.

- [ ] **Step 1: Write failing tests for default stability and one-row overrides**

Add imports for `asdict` and these tests to `EatLancetNormalizationTests`:

```python
def test_default_crosswalk_is_unchanged_when_overrides_are_omitted(self):
    implicit = [asdict(row) for row in build_crosswalk("2025", ROOT)]
    explicit = [
        asdict(row)
        for row in build_crosswalk(
            "2025",
            ROOT,
            density_overrides={},
            whole_grain_bread_share=None,
        )
    ]
    self.assertEqual(explicit, implicit)

def test_density_override_changes_only_its_destination(self):
    key = ("Fish, eggs & meat", "Fish & seafood")
    baseline = self.rows_by_key("2025")
    changed = {
        (row.pyramid_group, row.subitem): row
        for row in build_crosswalk(
            "2025", ROOT, density_overrides={key: 77.5 / 80.0}
        )
    }
    self.assertAlmostEqual(
        changed[key].normalized_g_per_day_at_reference_kcal,
        25.0 * 77.5 / 80.0,
    )
    for row_key in baseline.keys() - {key}:
        self.assertEqual(asdict(changed[row_key]), asdict(baseline[row_key]))

def test_whole_grain_share_must_be_between_zero_and_one(self):
    with self.assertRaisesRegex(ValueError, "whole_grain_bread_share"):
        build_crosswalk("2025", ROOT, whole_grain_bread_share=1.01)
```

- [ ] **Step 2: Run the new tests and verify RED**

Run:

```powershell
& 'C:\Users\risto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_eatlancet_normalization.EatLancetNormalizationTests.test_default_crosswalk_is_unchanged_when_overrides_are_omitted tests.test_eatlancet_normalization.EatLancetNormalizationTests.test_density_override_changes_only_its_destination tests.test_eatlancet_normalization.EatLancetNormalizationTests.test_whole_grain_share_must_be_between_zero_and_one -v
```

Expected: errors reporting that `build_crosswalk()` does not accept the new keyword arguments.

- [ ] **Step 3: Implement the minimal override seam**

Import `Mapping` and change the signature:

```python
from collections.abc import Mapping

FoodKey = tuple[str, str]

def build_crosswalk(
    edition: str,
    root: Path,
    *,
    density_overrides: Mapping[FoodKey, float] | None = None,
    whole_grain_bread_share: float | None = None,
) -> list[NormalizedRow]:
```

Inside `build_crosswalk`, normalize and validate inputs:

```python
overrides = dict(density_overrides or {})
if whole_grain_bread_share is not None and not 0 <= whole_grain_bread_share <= 1:
    raise ValueError("whole_grain_bread_share must be between 0 and 1")

def selected_density(destination: FoodKey, baseline: float) -> float:
    value = overrides.get(destination, baseline)
    if value <= 0:
        raise ValueError(f"Density must be positive for {destination}: {value}")
    return value
```

Use `whole_grain_bread_share` instead of `bread_share` when provided. Pass every density through `selected_density(destination, baseline_density)`, including the combined fruit/berry and nuts/seeds destinations. After building, reject unused override keys:

```python
known = {(row.pyramid_group, row.subitem) for row in output}
unknown = set(overrides) - known
if unknown:
    raise ValueError(f"Unknown density override destinations: {sorted(unknown)}")
```

- [ ] **Step 4: Verify GREEN and run the full normalization suite**

Run:

```powershell
& 'C:\Users\risto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_eatlancet_normalization -v
```

Expected: all normalization tests pass and the checked-in `data/crosswalk/eatlancet2025_crosswalk.csv` remains unchanged.

- [ ] **Step 5: Commit Task 1**

```powershell
git add -- src/eatlancet_normalization.py tests/test_eatlancet_normalization.py
git commit -m "feat: allow EAT conversion sensitivity overrides"
```

### Task 2: Create a traceable TAI candidate catalog

**Files:**
- Modify: `data/raw/tai/tabelraamat_table16_portion_grams.csv`
- Create: `data/crosswalk/eatlancet2025_sensitivity_candidates.csv`
- Create: `tests/test_eatlancet2025_sensitivity.py`
- Create: `src/eatlancet2025_sensitivity.py`

**Interfaces:**
- Produces: `FoodKey`, `ConversionVariant`, `load_candidates(root: Path) -> dict[FoodKey, list[ConversionVariant]]`, and `variant_crosswalk(root: Path, variant: ConversionVariant) -> list[NormalizedRow]`.
- `ConversionVariant` fields: `destination: FoodKey`, `name: str`, `grams_per_kcal: float | None`, `whole_grain_bread_share: float | None`, `source_kind: str`, `source_label: str`.

- [ ] **Step 1: Write failing provenance and coverage tests**

Create `tests/test_eatlancet2025_sensitivity.py` with:

```python
import csv
import unittest
from pathlib import Path

from src.eatlancet2025_sensitivity import load_candidates
from src.eatlancet_normalization import build_crosswalk

ROOT = Path(__file__).resolve().parents[1]

class EatLancet2025SensitivityTests(unittest.TestCase):
    def test_every_crosswalk_destination_has_candidates(self):
        expected = {
            (row.pyramid_group, row.subitem)
            for row in build_crosswalk("2025", ROOT)
        }
        self.assertEqual(set(load_candidates(ROOT)), expected)

    def test_tai_candidates_are_traceable_to_structured_table16(self):
        with (ROOT / "data/raw/tai/tabelraamat_table16_portion_grams.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            source_labels = {row["item_et"] for row in csv.DictReader(handle)}
        candidates = load_candidates(ROOT)
        for variants in candidates.values():
            for variant in variants:
                if variant.source_kind == "tai_table16":
                    self.assertIn(variant.source_label, source_labels)

    def test_grain_allocation_endpoints_are_explicit(self):
        candidates = load_candidates(ROOT)
        grain_variants = [
            variant
            for variants in candidates.values()
            for variant in variants
            if variant.source_kind == "grain_allocation"
        ]
        self.assertEqual(
            {variant.whole_grain_bread_share for variant in grain_variants},
            {0.0, 1.0},
        )
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```powershell
& 'C:\Users\risto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_eatlancet2025_sensitivity -v
```

Expected: import error because `src.eatlancet2025_sensitivity` does not exist.

- [ ] **Step 3: Complete the structured dairy source rows**

Append the four Table 16.3 rows already documented in `portion_gram_representative.csv`:

```csv
Dairy products,Kodujuust (cottage cheese),140,,,110,,Table 16.3 dairy subtype
Dairy products,Juust (cheese),55,,,110,,Table 16.3 dairy subtype
Dairy products,Koor (cream),100,,,110,,Table 16.3 dairy subtype
Dairy products,Magustatud piimatooted (flavoured dairy),300,,,110,,Table 16.3 dairy subtype
```

Keep the existing milk and 2.5%-fat yogurt rows. Do not include the lower-fat yogurt in this first analysis: the approved design limits dairy sensitivity to the six subtypes represented by the current baseline average.

- [ ] **Step 4: Create the candidate CSV**

Use these columns:

```csv
pyramid_group,subitem,variant_name,source_kind,source_label,portion_g,kcal_per_portion,whole_grain_bread_share,include_reason
```

Create rows for the current baseline plus these credible endpoints:

- vegetables: general vegetables only;
- legumes: cooked legumes only, because the output basis is edible/ready-to-eat;
- fruit+berries: general fruit, general berries, dried fruit low/high, and dried berries low/high;
- bread: bread range low/high and crispbread;
- porridge/pasta/rice: cooked porridge, quinoa/amaranth, couscous, and cooked pasta/rice; exclude dry flakes;
- potato: cooked potato and sweet potato;
- dairy: milk range low/high, cottage cheese, 2.5% yogurt, cheese, cream, and flavoured dairy;
- nuts/seeds: nuts, seeds, and cocoa;
- oils/fats: high-fat oil/spread, low-fat spread range low/high, pesto range low/high, avocado, olives range low/high, drained olive oil, hummus, and coconut/palm/lard; exclude the row with missing grams;
- fish: all fish/seafood rows with numeric grams, including published low/high endpoints;
- eggs: chicken egg only;
- poultry: the five poultry cut/skin rows used by the baseline; exclude liver and game;
- red meat: fresh pork/beef/lamb/veal range low/high and low-fat mince range low/high; exclude organs, tongue, salami, bacon, and high-fat mince because they change the production-category basis;
- sweets: sugar, honey, syrup, jam, chocolate/candy, coated nuts/fruit, hematogen, and sweetened muesli bars; exclude beverages.

Store the source `portion_g` and `kcal_per_portion` in the catalog; `load_candidates` derives `grams_per_kcal = portion_g / kcal_per_portion` and rejects non-positive inputs. Add two `grain_allocation` rows with `whole_grain_bread_share` 0 and 1 for each grain destination; `variant_crosswalk` applies the same allocation to the complete crosswalk, allowing both grain rows to receive extrema from the same recomputation.

- [ ] **Step 5: Implement candidate loading and single-variant execution**

Create the data classes and loader:

```python
from dataclasses import dataclass
from pathlib import Path
import csv

FoodKey = tuple[str, str]

@dataclass(frozen=True)
class ConversionVariant:
    destination: FoodKey
    name: str
    grams_per_kcal: float | None
    whole_grain_bread_share: float | None
    source_kind: str
    source_label: str

def load_candidates(root: Path) -> dict[FoodKey, list[ConversionVariant]]:
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
```

Execute one variant without mutating files:

```python
def variant_crosswalk(root: Path, variant: ConversionVariant):
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
```

- [ ] **Step 6: Verify GREEN**

Run:

```powershell
& 'C:\Users\risto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_eatlancet2025_sensitivity -v
```

Expected: the three provenance/coverage tests pass.

- [ ] **Step 7: Commit Task 2**

```powershell
git add -- data/raw/tai/tabelraamat_table16_portion_grams.csv data/crosswalk/eatlancet2025_sensitivity_candidates.csv src/eatlancet2025_sensitivity.py tests/test_eatlancet2025_sensitivity.py
git commit -m "feat: define EAT 2025 conversion variants"
```

### Task 3: Calculate food-group demand and self-sufficiency ranges

**Files:**
- Modify: `src/eatlancet2025_sensitivity.py`
- Modify: `tests/test_eatlancet2025_sensitivity.py`
- Create: `data/processed/eatlancet2025_conversion_sensitivity.csv`

**Interfaces:**
- Produces: `SensitivityResult`, `analyze(root: Path) -> list[SensitivityResult]`, and `write_csv(root: Path, rows: list[SensitivityResult]) -> Path`.
- `SensitivityResult` contains the exact output columns declared below.

- [ ] **Step 1: Write failing calculation and aggregation tests**

Add:

```python
from src.eatlancet2025_sensitivity import analyze

def test_single_value_mapping_has_zero_spread(self):
    rows = {(row.pyramid_group, row.subitem): row for row in analyze(ROOT)}
    eggs = rows[("Fish, eggs & meat", "Eggs")]
    self.assertEqual(eggs.min_g_per_day, eggs.baseline_g_per_day)
    self.assertEqual(eggs.max_g_per_day, eggs.baseline_g_per_day)

def test_fixed_production_makes_self_sufficiency_inverse_to_demand(self):
    for row in analyze(ROOT):
        if row.baseline_self_sufficiency_pct is None:
            self.assertIsNone(row.min_self_sufficiency_pct)
            self.assertIsNone(row.max_self_sufficiency_pct)
            continue
        self.assertLessEqual(row.min_demand_tonnes, row.baseline_demand_tonnes)
        self.assertGreaterEqual(row.max_demand_tonnes, row.baseline_demand_tonnes)
        self.assertAlmostEqual(
            row.min_self_sufficiency_pct,
            row.baseline_self_sufficiency_pct
            * row.baseline_demand_tonnes
            / row.max_demand_tonnes,
        )
        self.assertAlmostEqual(
            row.max_self_sufficiency_pct,
            row.baseline_self_sufficiency_pct
            * row.baseline_demand_tonnes
            / row.min_demand_tonnes,
        )

def test_analysis_covers_each_2025_row_once(self):
    keys = [(row.pyramid_group, row.subitem) for row in analyze(ROOT)]
    expected = [
        (row.pyramid_group, row.subitem)
        for row in build_crosswalk("2025", ROOT)
    ]
    self.assertEqual(keys, expected)
    self.assertEqual(len(keys), len(set(keys)))
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```powershell
& 'C:\Users\risto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_eatlancet2025_sensitivity -v
```

Expected: import error for `analyze` or missing `SensitivityResult` fields.

- [ ] **Step 3: Implement result calculation**

Define constants and result fields:

```python
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
```

Load `scenario_comparison.csv` by `(pyramid_group, subitem)`. Parse `scenario_C2_self_sufficiency_pct` only when it is a plain numeric point estimate; text bounds and blanks stay unresolved. Use `scenario_C2_demand_tonnes_per_year` as the reported baseline demand. Run each applicable variant, collect the affected row's `scaled_normalized_g_per_day_estonia`, and always include the baseline as an observation. For grain-allocation variants, collect both grain rows from the same recomputed crosswalk.

For each observation, preserve exact alignment with the checked-in C.2 baseline by scaling demand from the baseline ratio:

```python
variant_demand = scenario_c2_baseline_demand * variant_g / baseline_g
variant_self_sufficiency = (
    scenario_c2_baseline_self_sufficiency * scenario_c2_baseline_demand
    / variant_demand
    if scenario_c2_baseline_self_sufficiency is not None
    else None
)
```

Select minimum and maximum grams together with their variant labels, then compute `max_abs_change_g_per_day` as the larger absolute endpoint displacement and `max_relative_change_pct = 100 * max_abs_change_g_per_day / baseline_g`.

Threshold crossing is true when the closed interval spans the threshold:

```python
def crosses(low: float | None, high: float | None, threshold: float):
    if low is None or high is None:
        return None
    return low < threshold <= high
```

Do not cap percentages above 100.

- [ ] **Step 4: Implement deterministic CSV output**

Write `asdict(result)` rows with UTF-8 and `lineterminator="\n"`. Serialize unresolved numeric and threshold fields as empty strings. Use the baseline crosswalk order and stable rounding: grams to 3 decimals, tonnes and self-sufficiency to 1 decimal, changes to 1 decimal.

- [ ] **Step 5: Verify GREEN, generate, and check idempotence**

Run:

```powershell
& 'C:\Users\risto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_eatlancet2025_sensitivity -v
& 'C:\Users\risto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m src.eatlancet2025_sensitivity
git diff -- data/processed/eatlancet2025_conversion_sensitivity.csv
& 'C:\Users\risto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m src.eatlancet2025_sensitivity
git diff --exit-code -- data/processed/eatlancet2025_conversion_sensitivity.csv
```

Expected: tests pass, 14 result rows are written, and the second generation makes no change.

- [ ] **Step 6: Commit Task 3**

```powershell
git add -- src/eatlancet2025_sensitivity.py tests/test_eatlancet2025_sensitivity.py data/processed/eatlancet2025_conversion_sensitivity.csv
git commit -m "feat: calculate EAT 2025 conversion sensitivity"
```

### Task 4: Generate the Estonian findings report and verify isolation

**Files:**
- Modify: `src/eatlancet2025_sensitivity.py`
- Modify: `tests/test_eatlancet2025_sensitivity.py`
- Create: `docs/eatlancet2025_conversion_sensitivity_et.md`

**Interfaces:**
- Produces: `render_report(rows: list[SensitivityResult]) -> str` and `write_report(root: Path, rows: list[SensitivityResult]) -> Path`.

- [ ] **Step 1: Write failing report tests**

Add:

```python
from src.eatlancet2025_sensitivity import render_report

def test_report_numbers_come_from_analysis(self):
    rows = analyze(ROOT)
    report = render_report(rows)
    largest = max(rows, key=lambda row: row.max_relative_change_pct)
    self.assertIn(largest.subitem, report)
    self.assertIn(f"{largest.min_g_per_day:.1f}", report)
    self.assertIn(f"{largest.max_g_per_day:.1f}", report)
    self.assertIn("deterministlik tundlikkusvahemik", report)
    self.assertIn("ei ole usaldusvahemik", report.lower())

def test_analysis_does_not_modify_c2_or_dashboard_outputs(self):
    protected = [
        ROOT / "data/processed/scenario_comparison.csv",
        ROOT / "data/crosswalk/eatlancet2025_crosswalk.csv",
        ROOT / "output/dashboard_data_et.json",
        ROOT / "output/dashboard.html",
    ]
    before = {path: path.read_bytes() for path in protected}
    analyze(ROOT)
    self.assertEqual(before, {path: path.read_bytes() for path in protected})
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```powershell
& 'C:\Users\risto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_eatlancet2025_sensitivity -v
```

Expected: import error for `render_report`.

- [ ] **Step 3: Implement the report**

Render these sections from result objects, not hard-coded numbers:

```markdown
# EAT–Lancet 2025 → TAI teisenduse tundlikkus

## Mida testiti
## Suurima mõjuga toidugrupid
## Lävendite ületamised
## Millised järeldused püsivad
## Tõlgendamise piirid
```

List the five rows with the largest `max_relative_change_pct`, every 50% or 100% threshold crossing, and all rows where `min_g_per_day == max_g_per_day`. State explicitly that EAT energy, population energy, production, and trade behavior were not varied, and that the deterministic range is not a confidence interval (`ei ole usaldusvahemik`) or probability distribution. If no threshold crossing occurs, write that explicitly rather than omitting the section.

- [ ] **Step 4: Verify GREEN and regenerate both outputs**

Run:

```powershell
& 'C:\Users\risto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_eatlancet2025_sensitivity -v
& 'C:\Users\risto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m src.eatlancet2025_sensitivity
```

Expected: tests pass and both standalone outputs are written.

- [ ] **Step 5: Run full verification**

Run:

```powershell
& 'C:\Users\risto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_*.py'
& 'C:\Users\risto\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' tests/test_scenario_markers.cjs
& 'C:\Users\risto\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' tests/test_scorecard.cjs
git diff --check
```

Expected: all Python and JavaScript tests pass and `git diff --check` reports no whitespace errors in task-owned files.

- [ ] **Step 6: Review generated findings against the spec**

Confirm manually from the CSV:

- every C.2 crosswalk row appears exactly once;
- baseline lies inside every reported interval;
- min/max variant labels identify real catalog rows;
- unresolved rows have blank self-sufficiency bounds;
- report statements match the corresponding CSV values;
- no dashboard or Scenario C.2 artifact changed.

- [ ] **Step 7: Commit Task 4**

```powershell
git add -- src/eatlancet2025_sensitivity.py tests/test_eatlancet2025_sensitivity.py data/processed/eatlancet2025_conversion_sensitivity.csv docs/eatlancet2025_conversion_sensitivity_et.md
git commit -m "docs: report EAT 2025 conversion sensitivity"
```
