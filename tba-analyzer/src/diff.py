"""기존 레코드와 추출 레코드의 필드 단위 변경(diff)을 계산한다."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from . import csv_store as cs

# 변경 비교에서 제외하는 컬럼:
#   - No / System ID : 식별자 (변경 대상 아님)
#   - Last Update / 히스토리 : 메타/자동 갱신 컬럼
_IGNORE_FOR_DIFF = {
    cs.COL_NO,
    cs.COL_SYSTEM_ID,
    cs.COL_LAST_UPDATE,
    cs.COL_HISTORY,
}


@dataclass
class FieldChange:
    column: str
    before: str
    after: str


def _norm(v: str) -> str:
    return (v or "").strip()


def compute_changes(existing: Dict[str, str], extracted: Dict[str, str]) -> List[FieldChange]:
    """변경된 필드 목록을 반환한다.

    추출 레코드에 값이 비어있는 컬럼은 '정보 없음'으로 보고 덮어쓰지 않는다
    (센싱 누락으로 기존 정보를 지우는 사고 방지).
    """
    changes: List[FieldChange] = []
    for col in cs.COLUMNS:
        if col in _IGNORE_FOR_DIFF:
            continue
        after = _norm(extracted.get(col, ""))
        if not after:
            continue  # 빈 값은 덮어쓰지 않음
        before = _norm(existing.get(col, ""))
        if after != before:
            changes.append(FieldChange(column=col, before=before, after=after))
    return changes


def history_line(stamp: str, changes: List[FieldChange]) -> str:
    """히스토리 컬럼에 누적할 한 줄을 만든다.

    예) "[2026-06-24 15:30] 진행현황: 소 제기됨 → 진행중; 진행결과:  → 약식판결 기각"
    """
    parts = [f"{c.column}: {c.before or '∅'} → {c.after}" for c in changes]
    return f"[{stamp}] " + "; ".join(parts)
