"""accept 된 제안만 정본 CSV 에 반영하여 새 버전 파일을 생성한다.

원칙:
  - 기존 CSV 를 덮어쓰지 않고 새 타임스탬프 파일로 저장 (git 이력 = 감사 추적).
  - decision == 'accepted' 인 제안만 반영. 'pending'/'rejected' 는 무시.
  - UPDATE 는 변경 필드만 갱신하고 히스토리에 변경 이력을 누적(append).
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from . import csv_store as cs
from .diff import FieldChange, history_line


def _append_history(record: Dict[str, str], line: str) -> None:
    existing = (record.get(cs.COL_HISTORY, "") or "").strip()
    record[cs.COL_HISTORY] = (existing + "\n" + line).strip() if existing else line


def apply_changeset(
    base: cs.CanonicalCsv,
    changeset: Dict,
    *,
    stamp: str,
) -> Tuple[cs.CanonicalCsv, List[str]]:
    """accept 된 제안을 base 사본에 반영한다.

    반환: (수정된 CanonicalCsv, 적용 로그 목록)
    base 는 호출 전에 복제해서 넘기는 것을 권장(이 함수는 in-place 수정).
    """
    log: List[str] = []
    docket_idx = base.by_docket()
    sysid_idx = base.by_system_id()
    no_idx = {str(r.get(cs.COL_NO, "")).strip(): r for r in base.records}

    for p in changeset.get("proposals", []):
        if p.get("decision") != "accepted":
            continue

        if p["type"] == "NEW":
            rec = {c: p["record"].get(c, "") for c in cs.COLUMNS}
            # System ID 가 비어있으면 자동 발급 (없으면 round-trip 시 유효성 필터에 걸려 사라짐)
            if not str(rec.get(cs.COL_SYSTEM_ID, "")).strip():
                rec[cs.COL_SYSTEM_ID] = str(base.next_system_id())
            rec[cs.COL_LAST_UPDATE] = stamp
            created = base.append_record(rec)
            _append_history(created, history_line(stamp, [FieldChange("등록", "∅", "신규 소송 추가")]))
            log.append(f"[NEW]    No={created[cs.COL_NO]} {created.get(cs.COL_TITLE,'')[:40]}")

        elif p["type"] == "UPDATE":
            target = (
                docket_idx.get(cs.normalize_docket(p.get("match_key", "")))
                or sysid_idx.get(str(p.get("target_system_id", "")).strip())
                or no_idx.get(str(p.get("target_no", "")).strip())
            )
            if target is None:
                log.append(f"[SKIP]   UPDATE 대상 미발견 (key={p.get('match_key')})")
                continue
            changes = [FieldChange(**fc) for fc in p.get("field_changes", [])]
            for fc in changes:
                if fc.column in cs.COLUMNS:
                    target[fc.column] = fc.after
            target[cs.COL_LAST_UPDATE] = stamp
            _append_history(target, history_line(stamp, changes))
            log.append(
                f"[UPDATE] No={target.get(cs.COL_NO)} {target.get(cs.COL_TITLE,'')[:30]} "
                f"({len(changes)}개 필드)"
            )

    return base, log
