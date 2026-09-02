import unittest
from types import SimpleNamespace

from src.courtlistener import CLDocument
from src.complaint_parse import extract_dataset_names
from src.dataset_status import (
    build_dataset_status_section,
    build_dataset_status_section_from_comments,
    enrich_hits_with_complaint_documents,
)


class DatasetStatusTest(unittest.TestCase):
    def _complaint(self, text):
        return CLDocument(
            docket_id=1, docket_number="1:26-cv-1", case_name="Authors v. AI Corp.",
            court="N.D. Cal.", date_filed="2026-09-01", doc_type="Complaint",
            doc_number="1", description="Complaint",
            document_url="https://example.test/complaint", pdf_url="https://example.test/a.pdf",
            pdf_text_snippet=text, extracted_plaintiff="Authors", extracted_defendant="AI Corp.",
            extracted_causes="Copyright infringement", extracted_ai_snippet="",
        )

    def test_combines_case_hits_and_report_text(self):
        hits = [{
            "docket_id": 1,
            "caseName": "Authors v. AI Corp.",
            "docket_absolute_url": "/docket/1/example/",
            "snippet": "The complaint alleges Books3 was used for training.",
        }]

        section = build_dataset_status_section(
            hits, "The news report also explicitly identifies the LAION-5B dataset."
        )

        self.assertIn("식별된 데이터셋: 2종", section)
        self.assertIn("🔴 Books3", section)
        self.assertIn("Authors v. AI Corp.", section)
        self.assertIn("🔴 LAION-5B", section)

    def test_recognizes_datasets_frequently_named_in_training_disputes(self):
        text = (
            "The complaint identifies Library Genesis (LibGen), Z-Library, Bibliotik, "
            "Anna’s Archive, BookCorpus, OpenWebText, and the MS COCO dataset."
        )

        names = extract_dataset_names(text)

        for expected in (
            "LibGen", "Z-Library", "Bibliotik", "Anna's Archive", "BookCorpus",
            "OpenWebText", "MS COCO",
        ):
            self.assertIn(expected, names)

    def test_normalizes_generic_data_set_spelling(self):
        self.assertIn("Acme Research Dataset", extract_dataset_names("Acme Research Data Set"))

    def test_uses_full_complaint_text_joined_by_docket(self):
        hits = [{"docket_id": 9, "caseName": "Writer v. Model", "snippet": "Complaint"}]
        documents = [SimpleNamespace(
            docket_id=9,
            pdf_text_snippet="Defendant allegedly copied LibGen to assemble training data.",
        )]

        enriched = enrich_hits_with_complaint_documents(hits, documents)
        section = build_dataset_status_section(enriched, "")

        self.assertIn("🔴 LibGen", section)
        self.assertIn("Writer v. Model", section)
        self.assertNotIn("complaint_pdf_text", hits[0])

    def test_preserves_complaint_found_through_news_docket_lookup(self):
        document = SimpleNamespace(
            docket_id=10,
            docket_number="1:26-cv-10",
            case_name="Artist v. Image Co.",
            date_filed="2026-09-01",
            pdf_text_snippet="LAION-5B was allegedly scraped to train the image model.",
        )

        enriched = enrich_hits_with_complaint_documents([], [document])

        self.assertEqual(enriched[0]["docket_id"], 10)
        self.assertIn("LAION-5B", enriched[0]["complaint_pdf_text"])

    def test_complaint_document_provides_case_and_quoted_evidence(self):
        section = build_dataset_status_section(
            [], "", documents=[self._complaint(
                "Plaintiffs allege that defendant copied Books3 without permission to train its model."
            )]
        )

        self.assertIn("확인 근거", section)
        self.assertIn("[소장 원문](https://example.test/complaint)", section)
        self.assertIn("Plaintiffs allege", section)
        self.assertIn("copied Books3 without permission", section)
        self.assertIn("Authors v. AI Corp.", section)

    def test_report_only_name_is_clearly_marked_unverified(self):
        section = build_dataset_status_section([], "An article mentions LAION-5B.")

        self.assertIn("기사/요약에서 식별(소장 원문 미확인)", section)

    def test_consolidated_dataset_links_back_to_source_comment(self):
        section = build_dataset_status_section_from_comments([{
            "body": "The report says Books3 was used for training.",
            "html_url": "https://github.com/example/repo/issues/1#issuecomment-10",
        }])

        self.assertIn(
            "[출처](https://github.com/example/repo/issues/1#issuecomment-10)", section
        )
        self.assertIn("Books3 was used for training", section)

    def test_consolidated_dataset_prefers_complaint_link_in_row(self):
        section = build_dataset_status_section_from_comments([{
            "body": (
                "| 🔴 LibGen | [소장 원문](https://www.courtlistener.com/docket/1/doc/) "
                "| [원본 댓글](https://github.com/example/repo/issues/1#issuecomment-10) |"
            ),
            "html_url": "https://github.com/example/repo/issues/1#issuecomment-10",
        }])

        self.assertIn(
            "[출처](https://www.courtlistener.com/docket/1/doc/)", section
        )

    def test_multiple_source_links_are_preserved(self):
        section = build_dataset_status_section_from_comments([
            {"body": "Books3 appears in report one.", "html_url": "https://example.test/1"},
            {"body": "Books3 appears in report two.", "html_url": "https://example.test/2"},
        ])

        self.assertIn("[출처](https://example.test/1)", section)
        self.assertIn("[출처](https://example.test/2)", section)


if __name__ == "__main__":
    unittest.main()
