import csv
import json
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from src.dataset_catalog import catalog_as_json, upsert_dataset_catalog


class DatasetCatalogTest(unittest.TestCase):
    def test_upsert_keeps_one_dataset_and_accumulates_unique_details(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "catalog.csv"
            upsert_dataset_catalog({"books3": {
                "name": "Books3", "official_url": "https://example.test/books3",
                "cases": [("Authors v. AI", "https://example.test/case-1")],
                "evidence": [("Authors v. AI", "소장 원문", "Books3 copied", "https://example.test/doc-1")],
            }}, path, now="2026-09-01T00:00:00+00:00")
            upsert_dataset_catalog({"BOOKS3": {
                "name": "BOOKS3", "cases": [
                    ("Authors v. AI", "https://example.test/case-1"),
                    ("Writers v. Model", "https://example.test/case-2"),
                ],
                "evidence": [("Writers v. Model", "소장 검색문", "Books3 training", "https://example.test/doc-2")],
            }}, path, now="2026-09-02T00:00:00+00:00")

            rows = catalog_as_json(path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["dataset_name"], "Books3")
            self.assertEqual(rows[0]["case_count"], 2)
            self.assertEqual(rows[0]["evidence_count"], 2)
            self.assertEqual(rows[0]["first_seen"], "2026-09-01T00:00:00+00:00")
            self.assertEqual(rows[0]["last_seen"], "2026-09-02T00:00:00+00:00")

            with path.open(encoding="utf-8-sig", newline="") as handle:
                raw = list(csv.DictReader(handle))
            self.assertEqual(len(raw), 1)
            self.assertEqual(len(json.loads(raw[0]["related_cases"])), 2)

            # Re-seeing identical information must not create duplicate detail or
            # a noisy last_seen-only commit on every hourly monitor run.
            upsert_dataset_catalog({"books3": {
                "name": "books3", "cases": [("Authors v. AI", "https://example.test/case-1")],
                "evidence": [],
            }}, path, now="2026-09-03T00:00:00+00:00")
            unchanged = catalog_as_json(path)[0]
            self.assertEqual(unchanged["case_count"], 2)
            self.assertEqual(unchanged["last_seen"], "2026-09-02T00:00:00+00:00")

    def test_repeated_case_enriches_missing_urls_without_duplicate_rows(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "catalog.csv"
            upsert_dataset_catalog({"books3": {
                "name": "Books3", "cases": [("Authors v. AI", "")],
                "evidence": [("Authors v. AI", "기사", "Books3 copied", "")],
            }}, path, now="2026-09-01T00:00:00+00:00")
            upsert_dataset_catalog({"BOOKS3": {
                "name": "BOOKS3",
                "cases": [("Authors v. AI", "https://example.test/case")],
                "evidence": [("Authors v. AI", "소장 원문", "Books3 copied", "https://example.test/doc")],
            }}, path, now="2026-09-02T00:00:00+00:00")

            row = catalog_as_json(path)[0]
            self.assertEqual(len(row["related_cases"]), 1)
            self.assertEqual(row["related_cases"][0]["url"], "https://example.test/case")
            self.assertEqual(len(row["evidence"]), 1)
            self.assertEqual(row["evidence"][0]["url"], "https://example.test/doc")
            self.assertEqual(row["source_urls"], ["https://example.test/doc"])


if __name__ == "__main__":
    unittest.main()
