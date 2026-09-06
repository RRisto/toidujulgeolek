import unittest
from pathlib import Path

from build_treemap.build_sensitivity_chart import load_rows, render_chart


ROOT = Path(__file__).resolve().parents[1]


class EatLancetSensitivityChartTests(unittest.TestCase):
    def test_loads_all_sensitivity_rows_and_unresolved_values(self):
        rows = load_rows(ROOT)
        self.assertEqual(len(rows), 14)
        porridge = next(row for row in rows if row["subitem"].startswith("Porridges"))
        self.assertIsNone(porridge["baseline_self_sufficiency_pct"])
        self.assertEqual(porridge["min_g_per_day"], 0.0)

    def test_renders_two_panel_estonian_range_chart(self):
        html = render_chart(ROOT)
        self.assertIn("EAT–Lancet 2025 teisenduse tundlikkus", html)
        self.assertIn("Päevane kogus (g/päev)", html)
        self.assertIn("Isevarustatus (%)", html)
        self.assertIn("data-threshold=\"50\"", html)
        self.assertIn("data-threshold=\"100\"", html)
        self.assertEqual(html.count('class="chart-row"'), 14)
        self.assertIn("Kala ja mereannid", html)
        self.assertIn("Puuviljad ja marjad", html)
        self.assertIn("määramata", html)
        self.assertIn("nullnõudluse piir", html)

    def test_chart_is_self_contained_and_accessible(self):
        html = render_chart(ROOT)
        self.assertNotIn("https://", html)
        self.assertNotIn("fetch(", html)
        self.assertIn("prefers-color-scheme: dark", html)
        self.assertEqual(html.count('role="img"'), 28)
        self.assertNotIn("__", html)

    def test_chart_uses_compact_rows_and_prints_each_group_once(self):
        html = render_chart(ROOT)
        self.assertIn("min-height:44px", html)
        self.assertIn("height:32px", html)
        self.assertEqual(html.count('class="group-name"'), 6)
        self.assertEqual(html.count('class="group-spacer"'), 8)


if __name__ == "__main__":
    unittest.main()
