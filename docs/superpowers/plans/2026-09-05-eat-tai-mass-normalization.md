# EAT-Lancet to TAI Mass Normalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Normalize both EAT-Lancet scenarios onto the TAI edible-equivalent mass basis and regenerate every affected analysis and presentation artifact.

**Architecture:** A shared `src/eatlancet_normalization.py` module owns source reference values, weight-basis metadata, TAI representative energy densities, normalization, and CSV serialization for both editions. Existing Scenario C/C2 entry points become thin callers, and downstream scripts consume only `scaled_normalized_g_per_day_estonia`. Regression tests exercise source fidelity, energy conservation, demand propagation, and treemap aggregation before generated outputs and documentation are refreshed.

**Tech Stack:** Python 3 standard library (`csv`, `dataclasses`, `pathlib`, `unittest`), existing CSV/JSON build scripts, Node.js syntax checking for embedded dashboard JavaScript.

**Spec:** `docs/superpowers/specs/2026-09-05-eat-tai-mass-normalization-design.md`

## Global Constraints

- Preserve all published EAT source grams and calories alongside normalized values.
- Scenario A and Scenario B numerical inputs must not change.
- Scenario C/C2 gram and tonne consumers must use normalized edible-equivalent grams.
- EAT-Lancet 2025 source values are sugar 30 g, palm/coconut oil 6 g, and lard/tallow/butter 5 g.
- Include the known 50 g nuts value while labeling seeds/cocoa as unspecified.
- Exclude Honey from diet-mass totals because it is already included in the sweets/sugar aggregate.
- Do not stage, overwrite, or revert unrelated user changes in the dirty working tree.

---

### Task 1: Shared normalization engine

**Files:**
- Create: `src/eatlancet_normalization.py`
- Create: `tests/test_eatlancet_normalization.py`
- Modify: `src/scenario_c_eatlancet.py`
- Modify: `src/scenario_c2_eatlancet2025.py`
- Generate: `data/crosswalk/eatlancet_crosswalk.csv`
- Generate: `data/crosswalk/eatlancet2025_crosswalk.csv`

**Interfaces:**
- Produces: `build_crosswalk(edition: str, root: Path) -> list[NormalizedRow]`
- Produces: `write_crosswalk(edition: str, root: Path) -> Path`
- `NormalizedRow` fields: `pyramid_group`, `subitem`, `source_g_per_day`, `source_weight_basis`, `source_kcal_per_day`, `normalized_g_per_day_at_reference_kcal`, `scaled_normalized_g_per_day_estonia`, `normalization_method`
- Consumes: `data/crosswalk/portion_gram_representative.csv`, `data/processed/requirement_model_national.csv`, and `data/processed/tabelraamat_table13_portions.csv`

- [ ] **Step 1: Write failing source-fidelity and normalization tests**

```python
from pathlib import Path
import unittest

from src.eatlancet_normalization import build_crosswalk

ROOT = Path(__file__).resolve().parents[1]


class EatLancetNormalizationTests(unittest.TestCase):
    def test_2025_source_values_match_published_table(self):
        rows = {(r.pyramid_group, r.subitem): r for r in build_crosswalk("2025", ROOT)}
        sugar = rows[("Sweets, snacks & discretionary", "(total)")]
        oils = rows[("Nuts, seeds, oils & fats", "Oils/fats/spreads (rapeseed, representative)")]
        nuts = rows[("Nuts, seeds, oils & fats", "Nuts+Seeds,cocoa (combined)")]
        self.assertEqual(sugar.source_g_per_day, 30.0)
        self.assertEqual(nuts.source_g_per_day, 50.0)
        self.assertIn("palm/coconut oil 6", oils.normalization_method)
        self.assertIn("lard/tallow/butter 5", oils.normalization_method)

    def test_dry_categories_gain_ready_to_eat_mass(self):
        rows = {(r.pyramid_group, r.subitem): r for r in build_crosswalk("2019", ROOT)}
        porridge = rows[("Grain products & potatoes", "Porridges/pasta/rice/grain products")]
        legumes = rows[("Vegetables, fruits & berries", "Legumes")]
        self.assertGreater(porridge.normalized_g_per_day_at_reference_kcal, porridge.source_g_per_day)
        self.assertGreater(legumes.normalized_g_per_day_at_reference_kcal, legumes.source_g_per_day)

    def test_whole_grain_split_conserves_source_calories(self):
        rows = {(r.pyramid_group, r.subitem): r for r in build_crosswalk("2019", ROOT)}
        bread = rows[("Grain products & potatoes", "High-fibre bread/baked goods")]
        porridge = rows[("Grain products & potatoes", "Porridges/pasta/rice/grain products")]
        self.assertAlmostEqual(bread.source_kcal_per_day + porridge.source_kcal_per_day, 811.0, places=6)
```

- [ ] **Step 2: Run the tests and verify RED**

Run: `python -m unittest tests.test_eatlancet_normalization -v`

Expected: import failure because `src.eatlancet_normalization` does not exist.

- [ ] **Step 3: Implement the shared normalization model**

Create immutable `Edition` and `NormalizedRow` dataclasses. Store the verified 2019 and 2025 source grams, kcal, weight bases, and reference kcal in edition constants. Load TAI representative grams and kcal-per-portion by subitem, calculate combined-row energy density from `requirement_model_national.csv`, split whole-grain kcal using Scenario B bread/porridge implied-kcal shares, and reject missing or non-positive conversion inputs with `ValueError`.

The public API must be:

```python
def build_crosswalk(edition: str, root: Path) -> list[NormalizedRow]: ...

def write_crosswalk(edition: str, root: Path) -> Path: ...

def main(edition: str) -> None: ...
```

CSV columns must exactly follow the `NormalizedRow` field order stated above.

- [ ] **Step 4: Convert the edition scripts into thin entry points**

`src/scenario_c_eatlancet.py` calls `main("2019")`; `src/scenario_c2_eatlancet2025.py` calls `main("2025")`. Retain concise source citations in module docstrings and remove duplicate hard-coded dictionaries.

- [ ] **Step 5: Run the focused tests and verify GREEN**

Run: `python -m unittest tests.test_eatlancet_normalization -v`

Expected: all normalization tests pass.

- [ ] **Step 6: Generate both crosswalks and inspect their contracts**

Run:

```powershell
python src/scenario_c_eatlancet.py
python src/scenario_c2_eatlancet2025.py
Get-Content data/crosswalk/eatlancet_crosswalk.csv -TotalCount 4
Get-Content data/crosswalk/eatlancet2025_crosswalk.csv -TotalCount 4
```

Expected: both headers expose source/basis/kcal/normalized/scaled-normalized fields; dry grain normalized mass exceeds source mass.

- [ ] **Step 7: Commit Task 1**

```powershell
git add src/eatlancet_normalization.py src/scenario_c_eatlancet.py src/scenario_c2_eatlancet2025.py tests/test_eatlancet_normalization.py data/crosswalk/eatlancet_crosswalk.csv data/crosswalk/eatlancet2025_crosswalk.csv
git commit -m "fix: normalize EAT diets to TAI edible mass"
```

---

### Task 2: Propagate normalized demand through analytical outputs

**Files:**
- Modify: `src/update_scenario_c.py`
- Modify: `src/update_scenario_c2.py`
- Modify: `src/patch_scenario_c2_special_cases.py`
- Modify: `src/update_flags_c.py`
- Modify: `src/update_flags_c2.py`
- Modify: `src/land_reallocation_analysis.py`
- Modify: `tests/test_eatlancet_normalization.py`
- Generate: `data/processed/scenario_comparison.csv`
- Generate: `data/processed/critical_dependency_flags.csv`
- Generate: `data/processed/land_reallocation_scenario.csv`

**Interfaces:**
- Consumes: crosswalk field `scaled_normalized_g_per_day_estonia`
- Produces: existing Scenario C/C2 CSV columns with recalculated demand ratios and self-sufficiency percentages
- Preserves: all Scenario A/B columns byte-for-byte at the parsed-value level

- [ ] **Step 1: Add a failing downstream propagation test**

Add a temporary-directory integration test that copies `scenario_comparison.csv`, loads a generated crosswalk, invokes a refactored `update_scenario(path, crosswalk_path, scenario)` function, and asserts:

```python
self.assertAlmostEqual(
    output_row["scenario_C_demand_tonnes_per_year"],
    normalized_g * 1_339_785 * 365 / 1_000_000,
    places=1,
)
self.assertEqual(output_row["scenario_A_demand_tonnes_per_year"], original_a_demand)
self.assertEqual(output_row["scenario_B_demand_tonnes_per_year"], original_b_demand)
```

- [ ] **Step 2: Run the downstream test and verify RED**

Run: `python -m unittest tests.test_eatlancet_normalization.EatLancetNormalizationTests.test_downstream_demand_uses_normalized_grams -v`

Expected: failure because current loaders require `scaled_g_per_day_estonia` and have no callable path-based update interface.

- [ ] **Step 3: Refactor Scenario C/C2 consumers minimally**

Make both update scripts read `scaled_normalized_g_per_day_estonia`, expose path-parameterized update functions for tests, and retain command-line behavior using repository-default paths. Update special-case notes and flags so nuts are a known partial mass, not missing, and 2025 sugar notes contain 30 g rather than 6 g.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `python -m unittest tests.test_eatlancet_normalization -v`

Expected: source, normalization, and propagation tests pass.

- [ ] **Step 5: Regenerate analytical CSVs in dependency order**

Run:

```powershell
python src/update_scenario_c.py
python src/update_flags_c.py
python src/update_scenario_c2.py
python src/patch_scenario_c2_special_cases.py
python src/update_flags_c2.py
python src/land_reallocation_analysis.py
```

Expected: scripts exit 0 and print recalculated C/C2 demand, self-sufficiency, flags, and land effects.

- [ ] **Step 6: Verify Scenario A/B immutability and C/C2 consistency**

Use a test fixture containing the pre-change Scenario A/B columns. Assert all 16 rows retain their original A/B parsed values. For every numeric C/C2 row, assert `self_sufficiency = scenario_A_pct * demand_A / demand_C_or_C2` within stored rounding.

- [ ] **Step 7: Commit Task 2**

```powershell
git add src/update_scenario_c.py src/update_scenario_c2.py src/patch_scenario_c2_special_cases.py src/update_flags_c.py src/update_flags_c2.py src/land_reallocation_analysis.py tests/test_eatlancet_normalization.py data/processed/scenario_comparison.csv data/processed/critical_dependency_flags.csv data/processed/land_reallocation_scenario.csv
git commit -m "fix: propagate normalized EAT demand"
```

---

### Task 3: Rebuild exports and non-duplicating treemaps

**Files:**
- Modify: `src/export_dashboard_data.py`
- Modify: `build_treemap/build_treemap.py`
- Create: `build_treemap/build_treemap_data.py`
- Modify: `build_treemap/build_treemap_data_et.py`
- Modify: `tests/test_eatlancet_normalization.py`
- Generate: `output/dashboard_data.json`
- Generate: `output/dashboard_data_et.json`
- Generate: `build_treemap/treemap_data.json`
- Generate: `build_treemap/treemap_data_et.json`
- Generate: `output/dashboard.html`
- Generate: `output/dashboard_et.html`
- Generate: `output/dashboard_et_v2.html`
- Generate: `output/diet_treemap.html`
- Generate: `output/diet_treemap_et.html`
- Generate: `output/secondary_effects.html`

**Interfaces:**
- `build_treemap_data(root: Path) -> dict` consumes canonical population `1_339_785` and dashboard demand tonnes
- Excludes: `(Sweets, snacks & discretionary, Honey)` from all treemap scenarios
- Produces: each scenario total exactly equal to the sum of emitted leaves

- [ ] **Step 1: Add failing treemap aggregation tests**

```python
from build_treemap.build_treemap_data import build_treemap_data

data = build_treemap_data(ROOT)
for scenario in data["scenarios"]:
    self.assertAlmostEqual(
        scenario["total_g_per_day"],
        sum(item["g_per_day"] for item in scenario["items"]),
        places=1,
    )
    self.assertNotIn("Honey", {item["item"] for item in scenario["items"]})
self.assertEqual(data["population"], 1_339_785)
```

- [ ] **Step 2: Run the treemap test and verify RED**

Run: `python -m unittest tests.test_eatlancet_normalization.EatLancetNormalizationTests.test_treemap_uses_canonical_population_and_excludes_honey -v`

Expected: import failure because `build_treemap_data.py` does not exist.

- [ ] **Step 3: Implement deterministic treemap-data generation**

Move the previously precomputed data derivation into `build_treemap/build_treemap_data.py`. Read `output/dashboard_data.json`, use `1_339_785`, omit structurally empty values and Honey, calculate normalized grams and percentages, sort deterministically, and write `treemap_data.json`. Keep `build_treemap.py` responsible only for embedding generated JSON in HTML.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `python -m unittest tests.test_eatlancet_normalization -v`

Expected: all tests pass, including exact treemap aggregation.

- [ ] **Step 5: Rebuild all dashboard and treemap outputs**

Run:

```powershell
python src/export_dashboard_data.py
python build_dashboard.py
python build_dashboard_et_v2.py
python src/dashboard/build_dashboard_et.py
python build_treemap/build_treemap_data.py
python build_treemap/build_treemap_data_et.py
python build_treemap/build_treemap.py
python build_treemap/build_treemap_et.py
```

Regenerate `output/secondary_effects.html` through its existing build path if it embeds land data; otherwise verify its moved-page banner remains data-free and unchanged.

- [ ] **Step 6: Validate generated artifacts**

Parse all four JSON files with Python. Extract inline scripts from the three dashboard HTML files and both treemap HTML files into temporary files, run `node --check` on each, and assert no unresolved `{{...}}`, `@@...@@`, or `__TREEMAP_DATA__` placeholders remain.

- [ ] **Step 7: Commit Task 3**

Stage only files changed by this task and commit:

```powershell
git commit -m "build: refresh normalized diet outputs"
```

---

### Task 4: Correct methodology and verify the complete branch

**Files:**
- Modify: `docs/methodology.md`
- Modify: `plans/PLAN.md`
- Modify: `plans/PHASE10_NOTES.md`
- Modify: `plans/PHASE14_NOTES.md`
- Modify: `plans/PHASE15_NOTES.md`
- Modify: `plans/PHASE20_NOTES.md`
- Modify: `README.md`
- Create: `plans/PHASE21_NOTES.md`

**Interfaces:**
- Documents: source versus normalized basis, formulas, source corrections, before/after totals, uncertainty, and all materially changed conclusions
- Marks: historical superseded figures rather than silently erasing their context

- [ ] **Step 1: Add documentation assertions**

Add a test that reads the current methodology and phase notes and requires the phrases `dry weight`, `normalized edible-equivalent`, `30 g/day`, and `Honey` plus the regenerated C/C2 total values. It must reject the obsolete claim `31g -> 6g` unless immediately marked `superseded`.

- [ ] **Step 2: Run the documentation test and verify RED**

Run: `python -m unittest tests.test_eatlancet_normalization.EatLancetNormalizationTests.test_documentation_records_normalized_basis -v`

Expected: failure because current documentation still presents the old mass comparison and 6 g sugar value.

- [ ] **Step 3: Update documentation and phase history**

Revise the current methodology and roadmap conclusions; add `PHASE21_NOTES.md` with the root cause, conversion contract, exact commands, before/after table, affected self-sufficiency/land results, verification evidence, and remaining limitations. Historical notes must clearly label old figures as superseded.

- [ ] **Step 4: Run documentation and full unit tests**

Run: `python -m unittest discover -s tests -v`

Expected: all tests pass with no failures or errors.

- [ ] **Step 5: Run complete generation pipeline once more**

Run all Task 1–3 generation commands from a clean process, followed by JSON parsing, `node --check`, `git diff --check`, and focused assertions that Scenario A/B values equal their captured baseline.

- [ ] **Step 6: Review the final diff for scope and generated consistency**

Confirm `git diff --name-only` contains only normalization source, tests, affected generated outputs, and listed documentation. Confirm unrelated pre-existing modifications remain unstaged and are not reverted.

- [ ] **Step 7: Commit Task 4**

```powershell
git add README.md docs/methodology.md plans/PLAN.md plans/PHASE10_NOTES.md plans/PHASE14_NOTES.md plans/PHASE15_NOTES.md plans/PHASE20_NOTES.md plans/PHASE21_NOTES.md tests/test_eatlancet_normalization.py
git commit -m "docs: explain normalized diet mass basis"
```

- [ ] **Step 8: Report branch results**

Report the branch name, commits, verified commands, before/after scenario totals, materially changed self-sufficiency or land conclusions, and any remaining uncertainty. Do not merge or push without a separate user request.
