from pathlib import Path
import unittest

from src.eatlancet_normalization import build_crosswalk


ROOT = Path(__file__).resolve().parents[1]


class EatLancetNormalizationTests(unittest.TestCase):
    def rows_by_key(self, edition: str):
        return {
            (row.pyramid_group, row.subitem): row
            for row in build_crosswalk(edition, ROOT)
        }

    def test_2025_source_values_match_published_table(self):
        rows = self.rows_by_key("2025")

        sugar = rows[("Sweets, snacks & discretionary", "(total)")]
        oils = rows[
            (
                "Nuts, seeds, oils & fats",
                "Oils/fats/spreads (rapeseed, representative)",
            )
        ]
        nuts = rows[
            ("Nuts, seeds, oils & fats", "Nuts+Seeds,cocoa (combined)")
        ]

        self.assertEqual(sugar.source_g_per_day, 30.0)
        self.assertEqual(sugar.source_kcal_per_day, 115.0)
        self.assertEqual(nuts.source_g_per_day, 50.0)
        self.assertEqual(oils.source_g_per_day, 51.0)
        self.assertEqual(oils.source_kcal_per_day, 455.0)

    def test_dry_categories_gain_ready_to_eat_mass(self):
        rows = self.rows_by_key("2019")

        porridge = rows[
            (
                "Grain products & potatoes",
                "Porridges/pasta/rice/grain products",
            )
        ]
        legumes = rows[("Vegetables, fruits & berries", "Legumes")]

        self.assertEqual(porridge.source_weight_basis, "dry")
        self.assertEqual(legumes.source_weight_basis, "dry")
        self.assertGreater(
            porridge.normalized_g_per_day_at_reference_kcal,
            porridge.source_g_per_day,
        )
        self.assertGreater(
            legumes.normalized_g_per_day_at_reference_kcal,
            legumes.source_g_per_day,
        )

    def test_whole_grain_split_conserves_source_calories(self):
        rows = self.rows_by_key("2019")

        bread = rows[
            ("Grain products & potatoes", "High-fibre bread/baked goods")
        ]
        porridge = rows[
            (
                "Grain products & potatoes",
                "Porridges/pasta/rice/grain products",
            )
        ]

        self.assertAlmostEqual(
            bread.source_kcal_per_day + porridge.source_kcal_per_day,
            811.0,
            places=6,
        )

    def test_normalized_sugar_preserves_its_source_energy(self):
        sugar = self.rows_by_key("2025")[
            ("Sweets, snacks & discretionary", "(total)")
        ]

        implied_kcal = sugar.normalized_g_per_day_at_reference_kcal / 12.6 * 40

        self.assertAlmostEqual(implied_kcal, 115.0, places=6)


if __name__ == "__main__":
    unittest.main()
