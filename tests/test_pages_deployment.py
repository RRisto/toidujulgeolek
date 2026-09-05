import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)


class PagesDeploymentTests(unittest.TestCase):
    def test_landing_page_links_to_all_public_visualizations(self):
        output = ROOT / "output"
        parser = LinkCollector()
        parser.feed((output / "index.html").read_text(encoding="utf-8"))

        expected = {
            "dashboard.html",
            "diet_bar_chart_et.html",
            "diet_treemap_et.html",
        }
        self.assertEqual(set(parser.links), expected)
        for target in expected:
            self.assertTrue((output / target).is_file())

    def test_pages_workflow_publishes_only_output_from_main(self):
        workflow = (ROOT / ".github/workflows/pages.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("branches: [main]", workflow)
        self.assertIn("pages: write", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("uses: actions/upload-pages-artifact@v4", workflow)
        self.assertIn("path: output", workflow)
        self.assertNotIn("path: '.'", workflow)


if __name__ == "__main__":
    unittest.main()
