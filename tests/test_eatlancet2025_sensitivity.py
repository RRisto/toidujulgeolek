import csv
import math
import unittest
from pathlib import Path

from src.eatlancet2025_sensitivity import analyze, load_candidates, write_csv
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
                self.assertTrue(math.isinf(row.max_self_sufficiency_pct))
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
