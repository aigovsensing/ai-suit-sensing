import unittest

from src.complaint_parse import extract_dataset_names
from src.dataset_status import build_dataset_status_section


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


if __name__ == "__main__":
    unittest.main()
