import unittest

from src.courtlistener import CLCaseSummary, CLDocument
from src.dedup import generate_consolidated_report
from src.extract import Lawsuit
from src.render import render_markdown


class RelatedDatasetTablesTest(unittest.TestCase):
    def _case(self, snippet="Books3 was used as training data."):
        return CLCaseSummary(
            docket_id=7,
            case_name="Author v. AI Corp.",
            docket_number="1:26-cv-00007",
            court="N.D. Cal.",
            court_short_name="N.D. Cal.",
            court_api_url="",
            status="Open",
            judge="Example Judge",
            nature_of_suit="820 Copyright",
            cause="Copyright infringement",
            complaint_doc_no="1",
            complaint_link="https://example.test/complaint.pdf",
            complaint_type="Complaint",
            recent_updates="2026-08-25",
            extracted_causes="Unauthorized AI training",
            extracted_ai_snippet=snippet,
        )

    def _document(self):
        return CLDocument(
            docket_id=7,
            docket_number="1:26-cv-00007",
            case_name="Author v. AI Corp.",
            court="N.D. Cal.",
            date_filed="2026-08-25",
            doc_type="Complaint",
            doc_number="1",
            description="Complaint",
            document_url="https://example.test/document",
            pdf_url="https://example.test/complaint.pdf",
            pdf_text_snippet="Books3 was copied for model training.",
            extracted_plaintiff="Author",
            extracted_defendant="AI Corp.",
            extracted_causes="Unauthorized AI training",
            extracted_ai_snippet="Books3 was used as training data.",
        )

    def test_news_and_cases_tables_highlight_identified_datasets(self):
        news = Lawsuit(
            update_or_filed_date="2026-08-25",
            case_title="Author v. AI Corp.",
            article_title="AI company trained on Books3",
            case_number="1:26-cv-00007",
            reason="Books3 was allegedly copied for training.",
            article_urls=["https://example.test/news"],
        )

        report = render_markdown([news], [self._document()], [self._case()], 1)

        self.assertIn("| 소송번호 | 관련 데이터셋 | 조건", report)
        self.assertIn("| Nature | 관련 데이터셋 | 감지 레벨⬇️ |", report)
        self.assertEqual(report.count("🔴 Books3"), 2)
        self.assertIn('style="color:#d32f2f;font-weight:700;"', report)

        consolidated = generate_consolidated_report([{"body": report}])
        self.assertIn("### 📰 통합 AI Suit News", consolidated)
        self.assertIn("### ⚖️ 통합 Cases (Courtlistener+RECAP)", consolidated)
        self.assertEqual(consolidated.count("관련 데이터셋"), 2)
        self.assertEqual(consolidated.count("🔴 Books3"), 2)

    def test_missing_dataset_uses_plain_dash(self):
        news = Lawsuit("2026-08-25", "A v. B", "AI lawsuit", "1:26-cv-1", "Copyright", [])
        report = render_markdown([news], [], [self._case(snippet="AI training")], 0)
        dataset_cells = [line for line in report.splitlines() if line.startswith("| 1 |")]

        self.assertEqual(len(dataset_cells), 2)
        self.assertTrue(all(" | - | " in line for line in dataset_cells))
        self.assertTrue(all("🔴" not in line for line in dataset_cells))


if __name__ == "__main__":
    unittest.main()
