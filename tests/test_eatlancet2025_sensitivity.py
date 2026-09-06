import csv
import unittest
from pathlib import Path

from src.eatlancet2025_sensitivity import (
    SensitivityResult,
    _crosses,
    _parse_point_estimate,
    analyze,
    load_candidates,
    render_report,
    write_csv,
    write_report,
)
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
            if row.min_demand_tonnes == 0:
                self.assertIsNone(row.max_self_sufficiency_pct)
            else:
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

    def test_csv_output_is_idempotent_and_rounds_changes_to_one_decimal(self):
        target = write_csv(ROOT, analyze(ROOT))
        first = target.read_bytes()
        write_csv(ROOT, analyze(ROOT))
        self.assertEqual(target.read_bytes(), first)
        with target.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        eggs = next(row for row in rows if row["subitem"] == "Eggs")
        self.assertEqual(eggs["max_abs_change_g_per_day"], "0.0")

    def test_sensitivity_result_has_exact_output_schema(self):
        self.assertEqual(
            list(SensitivityResult.__dataclass_fields__),
            [
                "pyramid_group", "subitem", "baseline_g_per_day",
                "min_g_per_day", "max_g_per_day", "baseline_demand_tonnes",
                "min_demand_tonnes", "max_demand_tonnes",
                "baseline_self_sufficiency_pct", "min_self_sufficiency_pct",
                "max_self_sufficiency_pct", "max_abs_change_g_per_day",
                "max_relative_change_pct", "min_variant", "max_variant",
                "crosses_50pct", "crosses_100pct", "method_note",
            ],
        )

    def test_baselines_match_exact_reported_scenario_c2_values(self):
        reported = {}
        with (ROOT / "data/processed/scenario_comparison.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            for source in csv.DictReader(handle):
                demand = source["scenario_C2_demand_tonnes_per_year"].strip()
                if demand:
                    reported[(source["pyramid_group"], source["subitem"])] = (
                        float(demand),
                        _parse_point_estimate(
                            source["scenario_C2_self_sufficiency_pct"]
                        ),
                    )
        for result in analyze(ROOT):
            self.assertEqual(
                (result.baseline_demand_tonnes, result.baseline_self_sufficiency_pct),
                reported[(result.pyramid_group, result.subitem)],
            )

    def test_point_estimate_parser_requires_entire_finite_numeric_cell(self):
        for value, expected in [
            (" 173.9 ", 173.9), ("1e2", 100.0), ("", None),
            ("≤156.2% upper bound", None), ("173.9%", None),
            ("nan", None), ("-inf", None),
        ]:
            self.assertEqual(_parse_point_estimate(value), expected)

    def test_threshold_crossing_uses_closed_upper_boundary(self):
        self.assertFalse(_crosses(50.0, 50.0, 50.0))
        self.assertTrue(_crosses(49.9, 50.0, 50.0))
        self.assertIsNone(_crosses(None, 50.0, 50.0))

    def test_baseline_wins_equal_extrema_labels(self):
        rows = {(row.pyramid_group, row.subitem): row for row in analyze(ROOT)}
        eggs = rows[("Fish, eggs & meat", "Eggs")]
        self.assertEqual((eggs.min_variant, eggs.max_variant), ("baseline", "baseline"))

    def test_variants_only_affect_their_destination_except_grain_allocation(self):
        rows = {(row.pyramid_group, row.subitem): row for row in analyze(ROOT)}
        candidates = load_candidates(ROOT)
        grain_keys = {
            ("Grain products & potatoes", "High-fibre bread/baked goods"),
            ("Grain products & potatoes", "Porridges/pasta/rice/grain products"),
        }
        for key, result in rows.items():
            allowed = {"baseline"} | {variant.name for variant in candidates[key]}
            if key in grain_keys:
                allowed |= {
                    variant.name
                    for variants in candidates.values()
                    for variant in variants
                    if variant.source_kind == "grain_allocation"
                }
            self.assertIn(result.min_variant, allowed)
            self.assertIn(result.max_variant, allowed)

    def test_csv_has_14_rows_schema_and_baseline_crosswalk_order(self):
        target = write_csv(ROOT, analyze(ROOT))
        with target.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
        self.assertEqual(reader.fieldnames, list(SensitivityResult.__dataclass_fields__))
        self.assertEqual(len(rows), 14)
        self.assertEqual(
            [(row["pyramid_group"], row["subitem"]) for row in rows],
            [(row.pyramid_group, row.subitem) for row in build_crosswalk("2025", ROOT)],
        )

    def test_unresolved_and_zero_demand_fields_serialize_as_blanks(self):
        target = write_csv(ROOT, analyze(ROOT))
        with target.open(encoding="utf-8", newline="") as handle:
            rows = {
                (row["pyramid_group"], row["subitem"]): row
                for row in csv.DictReader(handle)
            }
        legumes = rows[("Vegetables, fruits & berries", "Legumes")]
        self.assertEqual(legumes["baseline_self_sufficiency_pct"], "")
        self.assertEqual(legumes["crosses_50pct"], "")
        bread = rows[("Grain products & potatoes", "High-fibre bread/baked goods")]
        self.assertEqual(bread["min_demand_tonnes"], "0.0")
        self.assertEqual(bread["max_self_sufficiency_pct"], "")
        self.assertEqual(bread["crosses_100pct"], "True")

    def test_report_numbers_come_from_analysis(self):
        rows = analyze(ROOT)
        report = render_report(rows)
        largest = max(rows, key=lambda row: row.max_relative_change_pct)
        self.assertIn(largest.subitem, report)
        self.assertIn(f"{largest.min_g_per_day:.1f}", report)
        self.assertIn(f"{largest.max_g_per_day:.1f}", report)
        self.assertIn("deterministlik tundlikkusvahemik", report)
        self.assertIn("ei ole usaldusvahemik", report.lower())

    def test_report_lists_all_threshold_crossings_and_zero_spread_rows(self):
        rows = analyze(ROOT)
        report = render_report(rows)
        for row in rows:
            if row.crosses_50pct or row.crosses_100pct:
                self.assertIn(row.subitem, report)
            if row.min_g_per_day == row.max_g_per_day:
                self.assertIn(row.subitem, report)
        self.assertIn("EAT-Lancet'i energia", report)
        self.assertIn("rahvastiku energiavajadust", report)
        self.assertIn("tootmist", report)
        self.assertIn("kaubanduskäitumist", report)

    def test_report_output_is_idempotent(self):
        rows = analyze(ROOT)
        target = write_report(ROOT, rows)
        first = target.read_bytes()
        self.assertEqual(target, ROOT / "docs/eatlancet2025_conversion_sensitivity_et.md")
        write_report(ROOT, rows)
        self.assertEqual(target.read_bytes(), first)

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
