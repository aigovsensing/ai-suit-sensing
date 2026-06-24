"""변경 제안(changeset) 직렬화/역직렬화.

제안은 JSON 으로 저장되며, 이 단계까지는 정본 CSV 에 절대 반영하지 않는다.
사람 검토(accept/reject) 후 apply 단계에서만 반영된다.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from typing import Dict, List

from . import csv_store as cs
from .matcher import MatchResult


def build_changeset(
    match_results: List[MatchResult],
    *,
    source_issue: str,
    base_csv: str,
    generated_at: str,
) -> Dict:
    """MatchResult 목록을 직렬화 가능한 changeset dict 로 변환한다.

    UNCHANGED 는 제안에서 제외한다.
    모든 제안의 기본 decision 은 'pending' (사람 검토 대기).
    """
    proposals: List[Dict] = []
    pid = 0
    for mr in match_results:
        if mr.type == "UNCHANGED":
            continue
        pid += 1
        item: Dict = {
            "id": f"p{pid}",
            "type": mr.type,
            "match_key": mr.match_key,
            "confidence": round(mr.confidence, 3),
            "decision": "pending",  # pending | accepted | rejected
        }
        if mr.type == "NEW":
            item["record"] = {c: mr.extracted.get(c, "") for c in cs.COLUMNS}
        else:  # UPDATE
            item["target_system_id"] = (mr.matched or {}).get(cs.COL_SYSTEM_ID, "")
            item["target_no"] = (mr.matched or {}).get(cs.COL_NO, "")
            item["field_changes"] = [asdict(fc) for fc in (mr.field_changes or [])]
        proposals.append(item)

    return {
        "generated_at": generated_at,
        "source_issue": source_issue,
        "base_csv": base_csv,
        "summary": {
            "new": sum(1 for p in proposals if p["type"] == "NEW"),
            "update": sum(1 for p in proposals if p["type"] == "UPDATE"),
        },
        "proposals": proposals,
    }


def save_changeset(changeset: Dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(changeset, f, ensure_ascii=False, indent=2)


def load_changeset(path: str) -> Dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)
