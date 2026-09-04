import re
import unittest
from pathlib import Path


OVERVIEW = Path(__file__).parents[1] / "frontend" / "overview.html"


class OverviewExportControlsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = OVERVIEW.read_text(encoding="utf-8")

    def test_each_board_has_all_four_prominent_save_controls(self):
        for board in ("datasets", "cases"):
            for file_type in ("csv", "xlsx", "docx", "pdf"):
                control = f'onclick="exportBoard(\'{board}\',\'{file_type}\')"'
                self.assertEqual(self.html.count(control), 1, control)
        self.assertEqual(self.html.count("⬇ 파일로 저장"), 2)

    def test_export_uses_full_filtered_results(self):
        export_function = re.search(
            r"function exportData\(kind\) \{(?P<body>.*?)\n\}", self.html, re.DOTALL
        )
        self.assertIsNotNone(export_function)
        body = export_function.group("body")
        self.assertIn("filteredDatasets()", body)
        self.assertIn("filteredCases()", body)


if __name__ == "__main__":
    unittest.main()
