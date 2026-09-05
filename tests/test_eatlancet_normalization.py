from pathlib import Path
import csv
import shutil
import tempfile
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

    def test_downstream_demand_uses_normalized_grams(self):
        from src.update_scenario_c import update_scenario

        source = ROOT / "data/processed/scenario_comparison.csv"
        crosswalk = ROOT / "data/crosswalk/eatlancet_crosswalk.csv"
        with tempfile.TemporaryDirectory() as directory:
            scenario_path = Path(directory) / "scenario_comparison.csv"
            shutil.copyfile(source, scenario_path)

            with source.open(encoding="utf-8", newline="") as handle:
                before = list(csv.DictReader(handle))
            update_scenario(scenario_path, crosswalk, "C")
            with scenario_path.open(encoding="utf-8", newline="") as handle:
                after = list(csv.DictReader(handle))
            with crosswalk.open(encoding="utf-8", newline="") as handle:
                normalized = {
                    (row["pyramid_group"], row["subitem"]): float(
                        row["scaled_normalized_g_per_day_estonia"]
                    )
                    for row in csv.DictReader(handle)
                }

        key = ("Vegetables, fruits & berries", "Vegetables")
        original = next(
            row for row in before if (row["pyramid_group"], row["subitem"]) == key
        )
        output = next(
            row for row in after if (row["pyramid_group"], row["subitem"]) == key
        )
        expected_tonnes = normalized[key] * 1_339_785 * 365 / 1_000_000
        self.assertAlmostEqual(
            float(output["scenario_C_demand_tonnes_per_year"]),
            expected_tonnes,
            places=1,
        )
        self.assertEqual(
            output["scenario_A_demand_tonnes_per_year"],
            original["scenario_A_demand_tonnes_per_year"],
        )
        self.assertEqual(
            output["scenario_B_demand_tonnes_per_year"],
            original["scenario_B_demand_tonnes_per_year"],
        )

    def test_both_eat_updates_preserve_all_a_and_b_values(self):
        from src.update_scenario_c import update_scenario

        source = ROOT / "data/processed/scenario_comparison.csv"
        with tempfile.TemporaryDirectory() as directory:
            scenario_path = Path(directory) / "scenario_comparison.csv"
            shutil.copyfile(source, scenario_path)
            with source.open(encoding="utf-8", newline="") as handle:
                before = list(csv.DictReader(handle))

            update_scenario(
                scenario_path,
                ROOT / "data/crosswalk/eatlancet_crosswalk.csv",
                "C",
            )
            update_scenario(
                scenario_path,
                ROOT / "data/crosswalk/eatlancet2025_crosswalk.csv",
                "C2",
            )
            with scenario_path.open(encoding="utf-8", newline="") as handle:
                after = list(csv.DictReader(handle))

        protected = [
            field
            for field in before[0]
            if field.startswith("scenario_A")
            or field.startswith("scenario_B")
            or field == "demand_change_ratio_B_over_A"
        ]
        for old, new in zip(before, after, strict=True):
            self.assertEqual(
                {field: old[field] for field in protected},
                {field: new[field] for field in protected},
            )

        for row in after:
            a_pct = self._float(row["scenario_A_self_sufficiency_pct"])
            a_demand = self._float(row["scenario_A_demand_tonnes_per_year"])
            for scenario in ("C", "C2"):
                demand = self._float(
                    row[f"scenario_{scenario}_demand_tonnes_per_year"]
                )
                pct = self._float(row[f"scenario_{scenario}_self_sufficiency_pct"])
                if None not in (a_pct, a_demand, demand, pct) and demand:
                    self.assertAlmostEqual(pct, a_pct * a_demand / demand, places=1)

    @staticmethod
    def _float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def test_treemap_uses_canonical_population_and_excludes_honey(self):
        from build_treemap.build_treemap_data import build_treemap_data

        data = build_treemap_data(ROOT)
        self.assertEqual(data["population"], 1_339_785)
        for scenario in data["scenarios"]:
            self.assertAlmostEqual(
                scenario["total_g_per_day"],
                sum(item["g_per_day"] for item in scenario["items"]),
                places=6,
            )
            self.assertNotIn("Honey", {item["item"] for item in scenario["items"]})

    def test_scenario_updates_are_idempotent(self):
        from src.update_scenario_c import update_scenario

        with tempfile.TemporaryDirectory() as directory:
            scenario_path = Path(directory) / "scenario_comparison.csv"
            shutil.copyfile(
                ROOT / "data/processed/scenario_comparison.csv", scenario_path
            )
            for scenario, filename in (
                ("C", "eatlancet_crosswalk.csv"),
                ("C2", "eatlancet2025_crosswalk.csv"),
            ):
                crosswalk = ROOT / "data/crosswalk" / filename
                update_scenario(scenario_path, crosswalk, scenario)
                once = scenario_path.read_bytes()
                update_scenario(scenario_path, crosswalk, scenario)
                self.assertEqual(scenario_path.read_bytes(), once)

    def test_bar_chart_matrix_aligns_each_food_across_four_diets(self):
        from build_treemap.build_bar_chart import build_comparison_matrix

        data = build_comparison_matrix(ROOT, "en")
        self.assertEqual([item["key"] for item in data["scenarios"]], ["A", "B", "C", "C2"])
        self.assertNotIn("Honey", {row["item"] for row in data["rows"]})
        dairy = next(row for row in data["rows"] if row["label"] == "Dairy products")
        self.assertEqual(
            dairy["percentages"],
            {"A": 23.3, "B": 22.9, "C": 14.5, "C2": 13.4},
        )
        self.assertTrue(
            all(set(row["percentages"]) == {"A", "B", "C", "C2"} for row in data["rows"])
        )
        legumes = next(row for row in data["rows"] if row["label"] == "Legumes")
        self.assertIsNone(legumes["percentages"]["A"])

    def test_estonian_chart_has_no_units_or_placeholders(self):
        from build_treemap.build_bar_chart import build_chart

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "build_treemap").mkdir()
            (root / "output").mkdir()
            for filename in ("bar_chart_template.html", "treemap_data_et.json"):
                shutil.copyfile(
                    ROOT / "build_treemap" / filename,
                    root / "build_treemap" / filename,
                )
            output = build_chart(root, "et").read_text(encoding="utf-8")

        self.assertNotIn("g/päev", output)
        self.assertIn("Andmed puuduvad", output)
        self.assertNotRegex(output, r"__[A-Z_]+__")

    def test_compact_dot_chart_has_four_percentage_marks_per_food(self):
        from build_treemap.build_bar_chart import build_chart

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "build_treemap").mkdir()
            (root / "output").mkdir()
            for filename in ("bar_chart_template.html", "treemap_data.json"):
                shutil.copyfile(
                    ROOT / "build_treemap" / filename,
                    root / "build_treemap" / filename,
                )
            output = build_chart(root, "en").read_text(encoding="utf-8")

        self.assertEqual(output.count('data-mark="dot"'), 14 * 4 - 1)
        self.assertEqual(output.count('data-mark="missing"'), 1)
        self.assertIn("Data unavailable", output)
        self.assertEqual(output.count('data-lane="diet"'), 14 * 4)
        self.assertNotIn("g/day", output)
        self.assertNotIn("grams per day", output)

    def test_chart_uses_image_readable_type_scale(self):
        from build_treemap.build_bar_chart import build_chart

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "build_treemap").mkdir()
            (root / "output").mkdir()
            for filename in ("bar_chart_template.html", "treemap_data_et.json"):
                shutil.copyfile(
                    ROOT / "build_treemap" / filename,
                    root / "build_treemap" / filename,
                )
            output = build_chart(root, "et").read_text(encoding="utf-8")

        self.assertRegex(output, r"body\{[^}]*font:18px/")
        self.assertRegex(output, r"h1\{font-size:34px")
        self.assertRegex(output, r"\.group-title\{font-size:20px")
        self.assertRegex(output, r"\.ticks span\{[^}]*font-size:16px")
        self.assertRegex(output, r"\.dot::after\{[^}]*font-size:16px")
        self.assertRegex(output, r"\.plot\{height:34px")
        self.assertRegex(output, r"\.dot\{[^}]*width:12px;height:12px")

    def test_estonian_treemap_builder_preserves_utf8_labels(self):
        from build_treemap.build_treemap_data_et import build_et_data

        data = build_et_data(ROOT)
        groups = {
            item["group"]
            for scenario in data["scenarios"]
            for item in scenario["items"]
        }
        self.assertIn("Köögi- ja puuviljad, marjad", groups)
        self.assertIn("Pähklid, seemned, õlid ja rasvad", groups)


if __name__ == "__main__":
    unittest.main()
