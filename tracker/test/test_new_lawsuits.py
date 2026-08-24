from datetime import datetime, timezone
import unittest

from src.new_lawsuits import build_new_lawsuits_section


class NewLawsuitsDatasetTest(unittest.TestCase):
    def _hit(self, **overrides):
        hit = {
            "docket_id": 1,
            "caseName": "Author v. AI Corp.",
            "docketNumber": "1:26-cv-00001",
            "dateFiled": datetime.now(timezone.utc).date().isoformat(),
            "court_citation_string": "N.D. Cal.",
            "suitNature": "820 Copyright",
            "cause": "17:101 Copyright Infringement",
        }
        hit.update(overrides)
        return hit

    def test_named_dataset_and_complaint_allegation_are_rendered(self):
        body = build_new_lawsuits_section(
            lookback_days=3,
            hits=[self._hit(snippet="Plaintiff alleges Books3 was copied without permission as training data.")],
        )

        self.assertIn("관련 데이터셋: Books3", body)
        self.assertIn("소장문서 관련 주장:", body)
        self.assertIn("without permission", body)

    def test_no_named_dataset_is_explicitly_rendered(self):
        body = build_new_lawsuits_section(lookback_days=3, hits=[self._hit()])

        self.assertIn("관련 데이터셋: 해당 사항 없음", body)

    def test_structured_dataset_keeps_its_link(self):
        body = build_new_lawsuits_section(
            lookback_days=3,
            hits=[self._hit(related_datasets=[{
                "name": "Objaverse-XL",
                "url": "https://github.com/allenai/objaverse-xl",
            }])],
        )

        self.assertIn(
            "관련 데이터셋: [Objaverse-XL](https://github.com/allenai/objaverse-xl)", body
        )

    def test_known_dataset_gets_official_link_without_structured_metadata(self):
        body = build_new_lawsuits_section(
            lookback_days=3,
            hits=[self._hit(snippet="The complaint says Objaverse-XL was used for model training.")],
        )

        self.assertIn(
            "관련 데이터셋: [Objaverse-XL](https://github.com/allenai/objaverse-xl)", body
        )

    def test_structured_dataset_does_not_duplicate_detected_name(self):
        body = build_new_lawsuits_section(
            lookback_days=3,
            hits=[self._hit(
                snippet="Objaverse-XL was allegedly used for training.",
                related_datasets=[{
                    "name": "Objaverse-XL",
                    "url": "https://example.test/objaverse",
                }],
            )],
        )

        line = next(line for line in body.splitlines() if "관련 데이터셋:" in line)
        dataset_list = line.split("—", 1)[0]
        self.assertEqual(dataset_list.count("Objaverse-XL"), 1)
        self.assertIn("https://example.test/objaverse", line)


if __name__ == "__main__":
    unittest.main()
