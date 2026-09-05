import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.frames = []
        self._current_link = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a":
            href = attributes.get("href")
            if href:
                self._current_link = {"href": href, "text": ""}
                self.links.append(self._current_link)
        elif tag == "iframe":
            src = attributes.get("src")
            if src:
                self.frames.append(src)

    def handle_data(self, data):
        if self._current_link is not None:
            self._current_link["text"] += data

    def handle_endtag(self, tag):
        if tag == "a":
            self._current_link = None


class PagesDeploymentTests(unittest.TestCase):
    def test_landing_page_links_to_all_public_visualizations(self):
        output = ROOT / "output"
        parser = LinkCollector()
        parser.feed((output / "index.html").read_text(encoding="utf-8"))

        expected = [
            {
                "href": "dashboard.html",
                "text": "Toidujulgeoleku stsenaariumid",
            },
            {
                "href": "diet_comparison_et.html",
                "text": "Dieetide toidugruppide osakaalud",
            },
        ]
        self.assertEqual(parser.links, expected)
        for target in (link["href"] for link in expected):
            self.assertTrue((output / target).is_file())

    def test_combined_diet_page_contains_both_visualizations(self):
        output = ROOT / "output"
        parser = LinkCollector()
        parser.feed(
            (output / "diet_comparison_et.html").read_text(encoding="utf-8")
        )

        expected = ["diet_bar_chart_et.html", "diet_treemap_et.html"]
        self.assertEqual(parser.frames, expected)
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
