import unittest
from unittest.mock import patch

from src.digest_assembly import assemble_digest


class DigestAssemblyOrderTest(unittest.TestCase):
    @patch("src.digest_assembly.build_new_lawsuits_section", return_value="## 3. 신규 소송")
    @patch("src.digest_assembly.render_daily_news_section")
    @patch("src.digest_assembly.collect_daily_news", return_value=[])
    def test_dataset_status_is_the_first_section(
        self, _collect_news, render_news, _new_lawsuits
    ):
        render_news.side_effect = ["## 2. 기사", "## 2. 기사"]
        gemini = "## 🧠 (석간뉴스: 2026-08-28)\n\n## 1. 소송 요약"
        hits = [{"snippet": "Books3 was copied for AI training."}]

        github_body, email_body = assemble_digest(gemini, hits=hits)

        for body in (github_body, email_body):
            self.assertTrue(
                body.startswith("## 4. 🧬 소송사건에 연관된 데이터셋 현황")
            )
            self.assertLess(body.index("## 4."), body.index("## 🧠"))
            self.assertLess(body.index("## 🧠"), body.index("## 2."))
            self.assertLess(body.index("## 2."), body.index("## 3."))


if __name__ == "__main__":
    unittest.main()
