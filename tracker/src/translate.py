from __future__ import annotations
"""
기사 제목 번역 모듈 (영문 → 한글).

가독성 개선을 위해 영어 기사 제목을 한글로 번역한다. 별도의 API 키가 필요 없는
**무료 구글 번역 엔드포인트**(translate.googleapis.com, client=gtx)를 사용한다.
Google Alert / 구글 뉴스 RSS 수집과 동일하게 AI(LLM) 미사용.

설계 원칙:
  - 실패해도 파이프라인이 죽지 않도록 항상 안전하게 폴백한다.
    (네트워크 오류·차단·타임아웃 시 빈 문자열 반환 → 호출부는 원문만 노출)
  - 같은 세션에서 동일 제목을 여러 번 번역하지 않도록 메모리 캐시를 둔다.
  - 이미 한글이 포함된 제목(국내 기사)은 번역하지 않는다.
  - ENABLE_TITLE_TRANSLATION=0 으로 비활성화할 수 있다(기본 활성화).
"""
import os
import re
import json
import html
from typing import Dict

import requests

from .utils import debug_log

# 무료 구글 번역(웹) 엔드포인트 — API 키 불필요(client=gtx).
_GTX_URL = "https://translate.googleapis.com/translate_a/single"

# 동일 제목 재번역 방지를 위한 프로세스 메모리 캐시.
_CACHE: Dict[str, str] = {}

_HANGUL_RE = re.compile(r"[가-힣]")

# 번역 네트워크 타임아웃(초). RSS 수집과 유사하게 짧게 유지.
_TIMEOUT = float(os.environ.get("TITLE_TRANSLATE_TIMEOUT", "8") or "8")


def _enabled() -> bool:
    """번역 기능 활성화 여부. 기본 활성화, ENABLE_TITLE_TRANSLATION=0 이면 비활성화."""
    return (os.environ.get("ENABLE_TITLE_TRANSLATION", "1") or "1").strip() != "0"


def _looks_korean(text: str) -> bool:
    """이미 한글이 포함되어 있으면 번역 대상에서 제외한다."""
    return bool(_HANGUL_RE.search(text or ""))


def _parse_gtx(payload) -> str:
    """
    gtx 응답 파싱. 응답 형태:
        [[["번역문","원문",null,null, ...], ["번역문2","원문2", ...]], ...]
    첫 배열의 각 문장 조각(첫 요소)을 이어붙여 전체 번역문을 만든다.
    """
    try:
        segments = payload[0] or []
        out = "".join(seg[0] for seg in segments if seg and seg[0])
        return out.strip()
    except Exception:
        return ""


def translate_to_korean(text: str, source_lang: str = "en") -> str:
    """
    영문 제목을 한글로 번역한다.

    Returns:
        번역된 한글 문자열. 아래의 경우 빈 문자열("")을 반환한다:
          - 기능 비활성화
          - 입력이 비었거나 이미 한글 포함(국내 기사)
          - 네트워크/파싱 실패
          - 번역 결과가 원문과 사실상 동일(번역 실패로 간주)
    """
    text = (text or "").strip()
    if not text or not _enabled():
        return ""
    if _looks_korean(text):
        return ""

    if text in _CACHE:
        return _CACHE[text]

    params = {
        "client": "gtx",
        "sl": source_lang,
        "tl": "ko",
        "dt": "t",
        "q": text,
    }
    headers = {
        # 일부 환경에서 UA 없으면 차단될 수 있어 브라우저 UA를 붙인다.
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0 Safari/537.36"
        ),
    }

    try:
        resp = requests.get(_GTX_URL, params=params, headers=headers, timeout=_TIMEOUT)
        resp.raise_for_status()
        payload = json.loads(resp.text)
        translated = _parse_gtx(payload)
    except Exception as e:  # 네트워크 차단/타임아웃/파싱 실패 등 모든 예외를 흡수
        debug_log(f"[translate] 번역 실패(원문 유지): {e} :: {text[:60]!r}")
        _CACHE[text] = ""  # 재시도 폭주 방지를 위해 실패도 캐시
        return ""

    # HTML 엔티티가 섞여 오는 경우(예: &#39;) 복원
    translated = html.unescape(translated).strip()

    # 번역이 원문과 동일하면(고유명사/약어만으로 구성 등) 병기 이득이 없으므로 폴백
    if not translated or translated.strip().lower() == text.strip().lower():
        _CACHE[text] = ""
        return ""

    _CACHE[text] = translated
    return translated
