import unittest
from types import SimpleNamespace

from src.complaint_parse import extract_dataset_names
from src.dataset_status import build_dataset_status_section, enrich_hits_with_complaint_documents


class DatasetStatusTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
