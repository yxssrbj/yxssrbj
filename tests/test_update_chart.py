import unittest
from pathlib import Path
from xml.etree import ElementTree

from scripts.update_chart import chart_svg, weekly_counts


class ChartTest(unittest.TestCase):
    def test_groups_real_daily_counts_into_weeks(self):
        payload = {"data": {"user": {"contributionsCollection": {
            "contributionCalendar": {"weeks": [
                {"firstDay": "2026-10-18", "contributionDays": [
                    {"contributionCount": 1}, {"contributionCount": 2}]},
                {"firstDay": "2026-10-25", "contributionDays": [
                    {"contributionCount": 4}]},
            ]}}
        }}}

        self.assertEqual(weekly_counts(payload), [("2026-10-18", 3), ("2026-10-25", 4)])

    def test_renders_accessible_weekly_bars_and_trend(self):
        svg = chart_svg([("2026-10-18", 3), ("2026-10-25", 4)])
        root = ElementTree.fromstring(svg)
        ns = {"svg": "http://www.w3.org/2000/svg"}

        self.assertEqual(root.attrib["role"], "img")
        self.assertEqual(len(root.findall(".//svg:rect[@class='bar']", ns)), 2)
        self.assertIsNotNone(root.find(".//svg:path[@class='trend']", ns))
        self.assertIn("Week of 2026-10-18: 3 contributions", svg)
        self.assertIn("Week of 2026-10-25: 4 contributions", svg)

    def test_zero_contributions_remains_a_valid_chart(self):
        root = ElementTree.fromstring(chart_svg([("2026-10-18", 0)]))
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")

    def test_graphql_errors_are_not_hidden(self):
        with self.assertRaisesRegex(RuntimeError, "GitHub GraphQL"):
            weekly_counts({"errors": [{"message": "Forbidden"}]})

    def test_profile_links_to_scheduled_chart(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/weekly-chart.yml").read_text()
        readme = (root / "README.md").read_text()

        self.assertIn("schedule:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("python3 scripts/update_chart.py", workflow)
        self.assertIn("assets/contributions-per-week.svg", readme)


if __name__ == "__main__":
    unittest.main()
