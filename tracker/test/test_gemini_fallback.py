import os
import unittest
from unittest.mock import MagicMock, patch

from src.gemini import get_gemini_summary
from src.trend import generate_trend_summary


class GeminiFallbackTest(unittest.TestCase):
    def test_missing_key_returns_caller_fallback(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_gemini_summary("prompt", "local report"), "local report")

    def test_depleted_credit_stops_after_one_call(self):
        client = MagicMock()
        client.models.generate_content.side_effect = Exception(
            "code: 429, message: Your prepayment credits are depleted."
        )
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test"}, clear=True), \
                patch("src.gemini.genai.Client", return_value=client):
            self.assertEqual(get_gemini_summary("조간뉴스", "data-only report"), "data-only report")
        client.models.generate_content.assert_called_once()

    def test_morning_report_has_no_api_failure_notice_without_key(self):
        with patch.dict(os.environ, {}, clear=True):
            report = generate_trend_summary([], [], 2, report_date="2026-09-03")
        self.assertIn("수집 데이터 자동 정리", report)
        self.assertIn("제공된 신규 도켓 데이터가 없습니다", report)
        self.assertNotIn("Gemini API 호출 실패", report)


if __name__ == "__main__":
    unittest.main()
