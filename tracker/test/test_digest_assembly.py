import unittest

from src.digest_assembly import _prioritize_dataset_section


class DatasetSectionPriorityTest(unittest.TestCase):
    def test_dataset_status_moves_immediately_after_report_title(self):
        body = """## 🧠 (석간뉴스: 2026-08-28) 당일 요약

## 1. 핵심 요약

요약 내용

## 3. 신규 소송 제기 현황

소송 내용

## 4. 🧬 소송사건에 연관된 데이터셋 현황

데이터셋 핵심 내용
"""

        result = _prioritize_dataset_section(body)

        self.assertLess(result.index("데이터셋 현황"), result.index("## 1. 핵심 요약"))
        self.assertLess(result.index("데이터셋 현황"), result.index("## 3. 신규 소송"))
        self.assertTrue(result.startswith("## 🧠 (석간뉴스: 2026-08-28)"))
        self.assertEqual(result.count("데이터셋 현황"), 1)

    def test_body_without_dataset_status_is_unchanged(self):
        body = "## 🗓️ (조간뉴스: 2026-08-28)\n\n## 1. 핵심 요약\n\n내용"

        self.assertEqual(_prioritize_dataset_section(body), body)


if __name__ == "__main__":
    unittest.main()
