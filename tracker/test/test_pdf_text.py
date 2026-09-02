import unittest
from unittest.mock import Mock, patch

from src.pdf_text import extract_pdf_text


class PdfTextTest(unittest.TestCase):
    @patch("src.pdf_text.PdfReader")
    @patch("src.pdf_text.requests.get")
    def test_scans_beyond_first_ten_pages_for_dataset_evidence(self, get, reader):
        response = Mock(content=b"pdf")
        response.raise_for_status.return_value = None
        get.return_value = response
        pages = []
        for number in range(15):
            page = Mock()
            page.extract_text.return_value = (
                "Defendant copied Books3 into its model training data."
                if number == 14 else f"Procedural material page {number}."
            )
            pages.append(page)
        reader.return_value.pages = pages

        text = extract_pdf_text("https://example.test/complaint.pdf", max_chars=1200)

        self.assertIn("Books3", text)
        self.assertEqual(pages[14].extract_text.call_count, 1)


if __name__ == "__main__":
    unittest.main()
