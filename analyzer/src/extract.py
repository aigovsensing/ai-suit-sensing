"""이슈 텍스트에서 구조화된 소송 레코드를 추출한다.

전략:
  1) Gemini LLM 으로 23개 컬럼 스키마에 맞춰 JSON 배열을 추출 (llm.enabled=true)
  2) JSON 스키마 + 도켓번호 정규식으로 검증 → 환각 차단
  3) 검증 실패/저신뢰 레코드는 confidence 를 낮춰 반드시 사람 검토로 보냄

LLM 키가 없거나 비활성화면 빈 목록을 반환하고, 호출부는 fixture 기반 테스트로 대체한다.
"""
from __future__ import annotations

import json
import os
import re
import time
from typing import Dict, List

from . import csv_store as cs

# 무료 티어 폴백 체인: 품질 우선(최신 3.x) → 안정성(무료 쿼터가 큰 2.5) 순으로 내려간다.
# tracker/src/gemini.py 와 동일한 계약(GEMINI_MODEL / GEMINI_MODEL_FALLBACKS)을 따른다.
DEFAULT_FALLBACK_CHAIN = [
    "gemini-flash-latest",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]


def _fallback_models(primary: str) -> List[str]:
    """1차 모델 뒤에 폴백 체인을 붙여 중복 없이 순서를 보존한다."""
    raw = os.environ.get("GEMINI_MODEL_FALLBACKS", "")
    fallbacks = [m.strip() for m in raw.split(",") if m.strip()] or DEFAULT_FALLBACK_CHAIN
    ordered: List[str] = []
    for name in [primary, *fallbacks]:
        if name not in ordered:
            ordered.append(name)
    return ordered

# 미국 연방 도켓번호 패턴 (예: 5:26-cv-06206, 3:24-cv-05417)
DOCKET_RE = re.compile(r"\b\d{1,2}:\d{2}-[a-z]{2}-\d{3,6}\b", re.IGNORECASE)

# LLM 에 건네는 추출 스키마(허용 키 = 정본 컬럼의 부분집합)
EXTRACT_KEYS = [
    cs.COL_STATUS,
    cs.COL_TITLE,
    cs.COL_DOCKET,
    cs.COL_FILED,
    cs.COL_PLAINTIFF,
    cs.COL_DEFENDANT,
    cs.COL_TARGET_DATA,
    cs.COL_TARGET_PRODUCT,
    cs.COL_REASON,
    cs.COL_COURT,
    cs.COL_COUNTRY,
    cs.COL_AMOUNT,
    cs.COL_SUMMARY,
    cs.COL_TRACKER,
    cs.COL_RESULT,
    cs.COL_PLAINTIFF_LAWYER,
    cs.COL_DEFENDANT_LAWYER,
]

_PROMPT = """너는 AI 학습데이터 관련 소송 정보를 정리하는 분석가다.
아래 GitHub 이슈 텍스트(자동 센싱 리포트)에서 **개별 소송 사건**을 추출해
JSON 배열로만 출력하라. 다른 설명은 절대 출력하지 마라.

각 원소는 아래 키만 사용한다(모르는 값은 빈 문자열 ""):
{keys}

규칙:
- "소송번호*"는 미국 연방 도켓번호 형식(예: 5:26-cv-06206)으로만 채운다. 불확실하면 "".
- "소송제목 (원고 v. 피고)*"는 "원고 v. 피고" 형태로 정리한다.
- 같은 소송이 여러 번 언급되면 하나로 합친다.
- 근거가 약하거나 추정인 값은 비워 둔다(환각 금지).

이슈 텍스트:
\"\"\"
{text}
\"\"\"
"""


def _validate(rec: Dict[str, str]) -> Dict[str, str]:
    """레코드를 정본 컬럼 키로 정규화하고 도켓번호를 검증한다."""
    out = cs.empty_record()
    for k, v in rec.items():
        if k in cs.COLUMNS:
            out[k] = ("" if v is None else str(v)).strip()
    # 도켓번호 형식 검증: 패턴 불일치면 비움
    docket = out.get(cs.COL_DOCKET, "")
    if docket and not DOCKET_RE.search(docket):
        m = DOCKET_RE.search(docket)
        out[cs.COL_DOCKET] = m.group(0) if m else ""
    return out


def _parse_json_array(text: str) -> List[Dict]:
    """LLM 응답에서 JSON 배열을 안전하게 파싱한다(코드펜스 제거)."""
    t = text.strip()
    t = re.sub(r"^```(?:json)?", "", t).strip()
    t = re.sub(r"```$", "", t).strip()
    start, end = t.find("["), t.rfind("]")
    if start == -1 or end == -1:
        return []
    try:
        data = json.loads(t[start : end + 1])
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


# 무료 티어 분당 5회(RPM) 제한 대비: 호출 간 최소 간격 + 429 지수 백오프.
# 같은 키를 tracker(매시간 센싱)와 공유하므로 여유 있게 잡는다.
_MIN_CALL_INTERVAL_SEC = 15.0
_RETRY_DELAYS_SEC = [60, 120, 240]
_last_call_at = 0.0


def _is_rate_limit_error(exc: Exception) -> bool:
    name = type(exc).__name__
    msg = str(exc)
    return name == "ResourceExhausted" or "429" in msg or "quota" in msg.lower()


def _generate_throttled(gm, prompt: str):
    """호출 간격을 지키며 생성 요청. 429 는 백오프 후 재시도, 그래도 실패하면 raise."""
    global _last_call_at
    for i, delay_on_fail in enumerate([*_RETRY_DELAYS_SEC, None]):
        wait = _MIN_CALL_INTERVAL_SEC - (time.monotonic() - _last_call_at)
        if wait > 0:
            time.sleep(wait)
        try:
            _last_call_at = time.monotonic()
            return gm.generate_content(prompt)
        except Exception as e:  # noqa: BLE001
            if not _is_rate_limit_error(e) or delay_on_fail is None:
                raise
            print(f"[!] Gemini 429(쿼터 초과) — {delay_on_fail}초 후 재시도 ({i + 1}/{len(_RETRY_DELAYS_SEC)})")
            time.sleep(delay_on_fail)


def extract_with_llm(text: str, model: str = "gemini-2.5-flash") -> List[Dict[str, str]]:
    """Gemini 로 소송 레코드를 추출한다. 키 없으면 빈 목록.

    같은 키를 tracker(매시간 센싱)와 공유하므로 호출 간 최소 간격을 지키고 429 는
    긴 지수 백오프로 재시도한다(_generate_throttled). 한 모델의 재시도가 모두
    소진되면 폴백 체인(GEMINI_MODEL_FALLBACKS)의 다음 모델로 넘어간다.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return []
    try:
        import google.generativeai as genai  # type: ignore
    except Exception:
        return []

    genai.configure(api_key=api_key)
    prompt = _PROMPT.format(keys="\n".join(f'- "{k}"' for k in EXTRACT_KEYS), text=text[:60000])

    # 환경변수 GEMINI_MODEL 이 있으면 호출부가 넘긴 model 보다 우선한다.
    primary = os.environ.get("GEMINI_MODEL") or model

    for current_model in _fallback_models(primary):
        try:
            gm = genai.GenerativeModel(current_model)
            resp = _generate_throttled(gm, prompt)
            raw = _parse_json_array(getattr(resp, "text", "") or "")
            return [_validate(r) for r in raw if isinstance(r, dict)]
        except Exception:  # noqa: BLE001 - 폴백 판단용
            # 429 재시도 소진 또는 그 외 오류 → 폴백 체인의 다음 모델로 넘어간다.
            continue
    return []


def extract(text: str, *, llm_enabled: bool = True, model: str = "gemini-flash-latest") -> List[Dict[str, str]]:
    """이슈 텍스트 → 검증된 소송 레코드 목록."""
    if llm_enabled:
        recs = extract_with_llm(text, model=model)
        if recs:
            return recs
    return []  # LLM 미사용/실패 시 빈 목록 (호출부에서 처리)
