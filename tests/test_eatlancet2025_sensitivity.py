import csv
import shutil
import tempfile
import unittest
from dataclasses import replace
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
    def candidate_fixture(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        for relative in (
            "data/crosswalk/portion_gram_representative.csv",
            "data/processed/tabelraamat_table13_portions.csv",
            "data/processed/requirement_model_national.csv",
            "data/raw/tai/tabelraamat_table16_portion_grams.csv",
            "data/crosswalk/eatlancet2025_sensitivity_candidates.csv",
        ):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        path = root / "data/crosswalk/eatlancet2025_sensitivity_candidates.csv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        return root, path, rows

    @staticmethod
    def write_fixture_csv(path, rows):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def test_loader_rejects_unsupported_or_missing_tai_provenance(self):
        invalid = [
            {"source_label": "Nonexistent Table 16 source"},
            {"portion_g": "999"},
            {"kcal_per_portion": "999"},
            {"portion_g": "", "kcal_per_portion": ""},
            {"portion_g": "nan"},
            {"kcal_per_portion": "inf"},
            {"whole_grain_bread_share": "1"},
            {"source_kind": "unknown"},
        ]
        for changes in invalid:
            with self.subTest(changes=changes):
                root, path, rows = self.candidate_fixture()
                candidate = next(row for row in rows if row["source_kind"] == "tai_table16")
                candidate.update(changes)
                self.write_fixture_csv(path, rows)
                with self.assertRaises(ValueError):
                    load_candidates(root)

    def test_loader_rejects_ambiguous_table16_source_label(self):
        root, _, candidates = self.candidate_fixture()
        label = next(row["source_label"] for row in candidates if row["source_kind"] == "tai_table16")
        source = root / "data/raw/tai/tabelraamat_table16_portion_grams.csv"
        with source.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        rows.append(next(row.copy() for row in rows if row["item_et"] == label))
        self.write_fixture_csv(source, rows)
        with self.assertRaises(ValueError):
            load_candidates(root)

    def test_loader_rejects_invalid_grain_allocation_semantics(self):
        invalid = [
            {"pyramid_group": "Fish, eggs & meat", "subitem": "Eggs"},
            {"whole_grain_bread_share": ""},
            {"whole_grain_bread_share": "0.5"},
            {"portion_g": "25", "kcal_per_portion": "75"},
        ]
        for changes in invalid:
            with self.subTest(changes=changes):
                root, path, rows = self.candidate_fixture()
                candidate = next(row for row in rows if row["source_kind"] == "grain_allocation")
                candidate.update(changes)
                self.write_fixture_csv(path, rows)
                with self.assertRaises(ValueError):
                    load_candidates(root)

    def test_loader_rejects_baseline_overrides_and_invalid_pairs(self):
        invalid = [
            {"portion_g": "999"}, {"portion_g": "nan"},
            {"kcal_per_portion": "inf"}, {"portion_g": "0"},
            {"portion_g": ""}, {"whole_grain_bread_share": "1"},
        ]
        for changes in invalid:
            with self.subTest(changes=changes):
                root, path, rows = self.candidate_fixture()
                rows[0].update(changes)
                self.write_fixture_csv(path, rows)
                with self.assertRaises(ValueError):
                    load_candidates(root)

    def test_loader_preserves_91_candidates_and_accepts_empty_baselines(self):
        self.assertEqual(sum(map(len, load_candidates(ROOT).values())), 91)
        root, path, rows = self.candidate_fixture()
        for row in rows:
            if row["source_kind"] == "baseline":
                row.update(portion_g="", kcal_per_portion="")
        self.write_fixture_csv(path, rows)
        candidates = load_candidates(root)
        self.assertEqual(sum(map(len, candidates.values())), 91)
        for variants in candidates.values():
            baseline = next(variant for variant in variants if variant.source_kind == "baseline")
            self.assertIsNone(baseline.grams_per_kcal)

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

    def test_report_ranks_finite_self_sufficiency_movements_independently_of_demand(self):
        template = analyze(ROOT)[0]
        rows = [
            replace(
                template, subitem=f"Synthetic {index}",
                max_relative_change_pct=100 - index,
                baseline_self_sufficiency_pct=100,
                min_self_sufficiency_pct=100 - index,
                max_self_sufficiency_pct=100 + 10 * index,
            )
            for index in range(1, 8)
        ]
        report = render_report(rows)
        self.assertIn("## Suurimad isevarustuskindluse muutused", report)
        movements = report.split("## Suurimad isevarustuskindluse muutused")[1].split("##")[0]
        self.assertEqual(movements.count("- **"), 5)
        self.assertLess(movements.index("Synthetic 7"), movements.index("Synthetic 6"))
        self.assertIn("93.0–170.0 %", movements)
        self.assertIn("70.0 protsendipunkti", movements)
        self.assertNotIn("Synthetic 2", movements)
        self.assertNotIn("Synthetic 1", movements)

    def test_report_largest_finite_movement_includes_fish_from_actual_analysis(self):
        rows = analyze(ROOT)
        report = render_report(rows)
        self.assertIn("## Suurimad isevarustuskindluse muutused", report)
        movements = report.split("## Suurimad isevarustuskindluse muutused")[1].split("##")[0]
        first = movements.split("- **")[1]
        self.assertIn("Fish & seafood", first)
        fish = next(row for row in rows if row.subitem == "Fish & seafood")
        self.assertIn(f"{fish.max_self_sufficiency_pct - fish.baseline_self_sufficiency_pct:.1f} protsendipunkti", first)

    def test_report_classifications_follow_intervals_and_distinguish_unresolved_limits(self):
        template = analyze(ROOT)[0]
        values = [
            ("Always high", 110, 101, 120, 1),
            ("Always low", 20, 10, 49, 1),
            ("Middle", 70, 50, 100, 1),
            ("Crossing", 90, 40, 120, 1),
            ("Unresolved", None, None, None, 1),
            ("Zero demand", 110, 101, None, 0),
        ]
        rows = [
            replace(template, subitem=name, baseline_self_sufficiency_pct=base,
                    min_self_sufficiency_pct=low, max_self_sufficiency_pct=high,
                    min_demand_tonnes=demand)
            for name, base, low, high, demand in values
        ]
        report = render_report(rows)
        stable = report.split("## Millised järeldused püsivad")[1].split("##")[0]
        self.assertIn("üle 100%", stable)
        high_line = next(line for line in stable.splitlines() if "üle 100%" in line)
        low_line = next(line for line in stable.splitlines() if "alla 50%" in line)
        middle_line = next(line for line in stable.splitlines() if "50–100%" in line)
        self.assertIn("Always high", high_line)
        self.assertIn("101.0–120.0 %", high_line)
        self.assertIn("Always low", low_line)
        self.assertIn("10.0–49.0 %", low_line)
        self.assertIn("Middle", middle_line)
        for line in (high_line, low_line, middle_line):
            for excluded in ("Crossing", "Unresolved", "Zero demand"):
                self.assertNotIn(excluded, line)
        unresolved_line = next(line for line in stable.splitlines() if "punktihinnang puudub" in line)
        zero_line = next(line for line in stable.splitlines() if "nullnõudluse piir" in line)
        self.assertIn("Unresolved", unresolved_line)
        self.assertNotIn("Zero demand", unresolved_line)
        self.assertIn("Zero demand", zero_line)
        self.assertNotIn("Unresolved", zero_line)

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

    def test_report_retains_finite_self_sufficiency_endpoint_at_zero_demand(self):
        bread = next(
            row for row in analyze(ROOT)
            if row.subitem == "High-fibre bread/baked goods"
        )
        report = render_report(analyze(ROOT))
        self.assertIn(f"{bread.min_self_sufficiency_pct:.1f}%", report)
        self.assertIn("määramata nullnõudluse piir", report)
        self.assertIn(
            f"lähtetase {bread.baseline_self_sufficiency_pct:.1f}%", report
        )

    def test_report_uses_composite_identity_for_every_listed_row(self):
        rows = analyze(ROOT)
        report = render_report(rows)
        listed = [
            *sorted(rows, key=lambda row: row.max_relative_change_pct, reverse=True)[:5],
            *(row for row in rows if row.crosses_50pct or row.crosses_100pct),
            *(row for row in rows if row.min_g_per_day == row.max_g_per_day),
        ]
        for row in listed:
            self.assertIn(f"{row.pyramid_group} — {row.subitem}", report)

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
