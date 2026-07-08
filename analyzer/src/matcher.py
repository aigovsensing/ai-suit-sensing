"""추출된 소송 레코드를 정본 CSV 와 대조하여 분류한다.

분류 결과:
  - NEW       : 기존 CSV 에 없는 신규 소송
  - UPDATE    : 기존 레코드가 있고 변경된 필드가 있음
  - UNCHANGED : 기존 레코드와 동일 (제안에서 제외)

식별 우선순위:
  1) 도켓번호(소송번호*) 정규화 일치   → confidence 0.97
  2) System ID 일치                    → confidence 0.95
  3) 사건명 퍼지 매칭(임계값 이상)      → confidence = score/100
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from . import csv_store as cs
from . import diff as diffmod

try:
    from rapidfuzz import fuzz  # type: ignore

    _HAS_RAPIDFUZZ = True
except Exception:  # pragma: no cover - 폴백
    _HAS_RAPIDFUZZ = False


def _ratio(a: str, b: str) -> float:
    """0~100 유사도. rapidfuzz 없으면 difflib 폴백."""
    a, b = (a or "").strip().lower(), (b or "").strip().lower()
    if not a or not b:
        return 0.0
    if _HAS_RAPIDFUZZ:
        return float(fuzz.token_sort_ratio(a, b))
    import difflib

    return difflib.SequenceMatcher(None, a, b).ratio() * 100.0


@dataclass
class MatchResult:
    type: str  # NEW | UPDATE | UNCHANGED
    extracted: Dict[str, str]
    confidence: float
    matched: Optional[Dict[str, str]] = None  # 매칭된 기존 레코드 (UPDATE/UNCHANGED)
    field_changes: Optional[List[diffmod.FieldChange]] = None
    match_key: str = ""


def classify(
    extracted_cases: List[Dict[str, str]],
    base: cs.CanonicalCsv,
    fuzzy_threshold: float = 88.0,
) -> List[MatchResult]:
    """추출 레코드 목록을 분류한다."""
    results: List[MatchResult] = []
    for ex in extracted_cases:
        docket = cs.normalize_docket(ex.get(cs.COL_DOCKET, ""))
        sid = (ex.get(cs.COL_SYSTEM_ID, "") or "").strip()

        matched: Optional[Dict[str, str]] = None
        confidence = 0.0
        key = docket or sid or ex.get(cs.COL_TITLE, "")

        # 1) 도켓번호
        if docket and docket in base.by_docket():
            matched, confidence, key = base.by_docket()[docket], 0.97, docket
        # 2) System ID
        elif sid and sid in base.by_system_id():
            matched, confidence, key = base.by_system_id()[sid], 0.95, sid
        # 3) 퍼지 (사건명)
        else:
            best, best_score = None, 0.0
            for rec in base.records:
                s = _ratio(ex.get(cs.COL_TITLE, ""), rec.get(cs.COL_TITLE, ""))
                if s > best_score:
                    best, best_score = rec, s
            if best is not None and best_score >= fuzzy_threshold:
                matched, confidence = best, best_score / 100.0
                key = cs.normalize_docket(best.get(cs.COL_DOCKET, "")) or best.get(cs.COL_TITLE, "")

        if matched is None:
            results.append(
                MatchResult(type="NEW", extracted=ex, confidence=0.9, match_key=key)
            )
            continue

        changes = diffmod.compute_changes(matched, ex)
        if changes:
            results.append(
                MatchResult(
                    type="UPDATE",
                    extracted=ex,
                    confidence=confidence,
                    matched=matched,
                    field_changes=changes,
                    match_key=key,
                )
            )
        else:
            results.append(
                MatchResult(
                    type="UNCHANGED",
                    extracted=ex,
                    confidence=confidence,
                    matched=matched,
                    match_key=key,
                )
            )
    return results
