"""정본(canonical) CSV 로드/저장 모듈.

dashboard 가 읽는 `aisuit_YYYYMMDD[_HHMM].csv` 포맷을 그대로 보존한다.
포맷 규칙:
  - 1행: 제목 (예: "AI 데이터 소송 현황")
  - 2행: 추출기간 (예: "추출기간: 2025-06-27 17:34 ~ 2026-06-24 09:47")
  - 3행: 헤더 (23개 컬럼)
  - 4행~: 데이터 (유효 레코드 + 빈 번호 패딩 행)

저장 시에는 빈 번호 패딩 행을 제거하고 유효 레코드만 다시 쓴다.
(dashboard/collector/builder.py 의 build_from_csv() 가 빈 행을 무시하므로 안전하다.)
"""
from __future__ import annotations

import csv
import glob
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ── 정본 23개 컬럼 (3행 헤더와 정확히 일치해야 함) ─────────────────────────
COLUMNS: List[str] = [
    "No",
    "System ID",
    "진행현황",
    "소송제목 (원고 v. 피고)*",
    "소송번호*",
    "소송제기일*",
    "원고",
    "피고",
    "대상 데이터",
    "대상 제품",
    "소송이유",
    "법원",
    "국가*",
    "소송금액 (USD)",
    "개요 및 배경 (By Gauss)",
    "Tracker(업로드 시 제외)",
    "관련 주소 (초기)(업로드 시 제외)",
    "Last Update(업로드 시 제외)",
    "진행결과",
    "히스토리(업로드 시 제외)",
    "변호사(원고)",
    "변호사(피고)",
    "비고(업로드 시 제외)",
]

# 의미 기반 컬럼 상수 (코드에서 직접 참조)
COL_NO = "No"
COL_SYSTEM_ID = "System ID"
COL_STATUS = "진행현황"
COL_TITLE = "소송제목 (원고 v. 피고)*"
COL_DOCKET = "소송번호*"
COL_FILED = "소송제기일*"
COL_PLAINTIFF = "원고"
COL_DEFENDANT = "피고"
COL_TARGET_DATA = "대상 데이터"
COL_TARGET_PRODUCT = "대상 제품"
COL_REASON = "소송이유"
COL_COURT = "법원"
COL_COUNTRY = "국가*"
COL_AMOUNT = "소송금액 (USD)"
COL_SUMMARY = "개요 및 배경 (By Gauss)"
COL_TRACKER = "Tracker(업로드 시 제외)"
COL_RELATED_URL = "관련 주소 (초기)(업로드 시 제외)"
COL_LAST_UPDATE = "Last Update(업로드 시 제외)"
COL_RESULT = "진행결과"
COL_HISTORY = "히스토리(업로드 시 제외)"
COL_PLAINTIFF_LAWYER = "변호사(원고)"
COL_DEFENDANT_LAWYER = "변호사(피고)"
COL_REMARKS = "비고(업로드 시 제외)"

DEFAULT_TITLE = "AI 데이터 소송 현황"


def normalize_docket(value: str) -> str:
    """도켓번호를 비교용으로 정규화한다.

    예) " 5:26-CV-06206 " -> "5:26-cv-06206"
    공백 제거, 소문자화, 양끝 잡문자 제거.
    """
    if not value:
        return ""
    v = value.strip().lower()
    v = re.sub(r"\s+", "", v)
    return v


def empty_record() -> Dict[str, str]:
    """모든 컬럼이 빈 문자열인 레코드를 만든다."""
    return {c: "" for c in COLUMNS}


@dataclass
class CanonicalCsv:
    """정본 CSV 한 개를 메모리에 담는 컨테이너."""

    title_row: List[str]
    period_row: List[str]
    records: List[Dict[str, str]] = field(default_factory=list)

    # ── 식별/조회 헬퍼 ───────────────────────────────────────────────
    def by_docket(self) -> Dict[str, Dict[str, str]]:
        """정규화 도켓번호 -> 레코드. 빈 도켓은 제외."""
        idx: Dict[str, Dict[str, str]] = {}
        for r in self.records:
            key = normalize_docket(r.get(COL_DOCKET, ""))
            if key:
                idx[key] = r
        return idx

    def by_system_id(self) -> Dict[str, Dict[str, str]]:
        idx: Dict[str, Dict[str, str]] = {}
        for r in self.records:
            sid = (r.get(COL_SYSTEM_ID, "") or "").strip()
            if sid:
                idx[sid] = r
        return idx

    def max_no(self) -> int:
        nos = [int(r[COL_NO]) for r in self.records if str(r.get(COL_NO, "")).strip().isdigit()]
        return max(nos, default=0)

    def next_system_id(self) -> int:
        """신규 레코드용 System ID 발급(기존 최대값 + 1).

        기존 System ID 가 10자리 숫자(예: 5001369427)이므로 숫자 체계를 유지한다.
        """
        sids = [
            int(r[COL_SYSTEM_ID])
            for r in self.records
            if str(r.get(COL_SYSTEM_ID, "")).strip().isdigit()
        ]
        return (max(sids) + 1) if sids else 5000000001

    def append_record(self, record: Dict[str, str]) -> Dict[str, str]:
        """새 레코드를 추가하고 No 를 자동 발급한다."""
        rec = empty_record()
        rec.update({k: v for k, v in record.items() if k in COLUMNS})
        rec[COL_NO] = str(self.max_no() + 1)
        self.records.append(rec)
        return rec


def _is_valid_record(row: Dict[str, str]) -> bool:
    """유효 레코드 판정: 숫자 System ID + 비어있지 않은 소송제목."""
    sid = (row.get(COL_SYSTEM_ID, "") or "").strip()
    title = (row.get(COL_TITLE, "") or "").strip()
    return sid.isdigit() and bool(title)


def load(path: str) -> CanonicalCsv:
    """정본 CSV 파일을 읽어 CanonicalCsv 로 반환한다."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    if len(rows) < 3:
        raise ValueError(f"CSV 포맷 오류(행 부족): {path}")

    title_row = rows[0]
    period_row = rows[1]
    header = [h.strip() for h in rows[2]]
    if header != COLUMNS:
        raise ValueError(
            "CSV 헤더가 정본 스키마와 다릅니다.\n"
            f"  기대: {COLUMNS}\n  실제: {header}"
        )

    records: List[Dict[str, str]] = []
    for raw in rows[3:]:
        # 컬럼 수 보정 (부족/초과 모두 23개로 맞춤)
        cells = (list(raw) + [""] * len(COLUMNS))[: len(COLUMNS)]
        row = dict(zip(COLUMNS, cells))
        if _is_valid_record(row):
            records.append(row)
    return CanonicalCsv(title_row=title_row, period_row=period_row, records=records)


def save(csvobj: CanonicalCsv, path: str) -> None:
    """CanonicalCsv 를 정본 포맷(BOM 포함)으로 저장한다.

    빈 번호 패딩 행은 제거되고 유효 레코드만 기록된다.
    """
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow((csvobj.title_row + [""] * len(COLUMNS))[: len(COLUMNS)])
        w.writerow((csvobj.period_row + [""] * len(COLUMNS))[: len(COLUMNS)])
        w.writerow(COLUMNS)
        for r in csvobj.records:
            w.writerow([r.get(c, "") for c in COLUMNS])


def latest_csv_path(data_dir: str) -> Optional[str]:
    """data_dir 에서 가장 최신 aisuit_*.csv 경로를 반환한다.

    파일명에 타임스탬프(YYYYMMDD[_HHMM])가 들어있어 사전식 정렬 = 시간순.
    """
    candidates = sorted(glob.glob(os.path.join(data_dir, "aisuit_*.csv")))
    return candidates[-1] if candidates else None


def make_new_csv_name(base_dir: str, stamp: str) -> str:
    """새 버전 CSV 파일 경로를 만든다. stamp 예: '20260624_1530'."""
    return os.path.join(base_dir, f"aisuit_{stamp}.csv")
