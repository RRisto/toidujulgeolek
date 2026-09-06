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
