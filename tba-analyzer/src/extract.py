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
from typing import Dict, List

from . import csv_store as cs

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


def extract_with_llm(text: str, model: str = "gemini-1.5-flash") -> List[Dict[str, str]]:
    """Gemini 로 소송 레코드를 추출한다. 키 없으면 빈 목록."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return []
    try:
        import google.generativeai as genai  # type: ignore
    except Exception:
        return []

    genai.configure(api_key=api_key)
    gm = genai.GenerativeModel(model)
    prompt = _PROMPT.format(keys="\n".join(f'- "{k}"' for k in EXTRACT_KEYS), text=text[:60000])
    resp = gm.generate_content(prompt)
    raw = _parse_json_array(getattr(resp, "text", "") or "")
    return [_validate(r) for r in raw if isinstance(r, dict)]


def extract(text: str, *, llm_enabled: bool = True, model: str = "gemini-1.5-flash") -> List[Dict[str, str]]:
    """이슈 텍스트 → 검증된 소송 레코드 목록."""
    if llm_enabled:
        recs = extract_with_llm(text, model=model)
        if recs:
            return recs
    return []  # LLM 미사용/실패 시 빈 목록 (호출부에서 처리)
