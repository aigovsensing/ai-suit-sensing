import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import csv_store as cs
from src.pr_review import validate_proposal


STAMP = "20260903_0539"
TITLE = f"🤖 소송 데이터 갱신 제안 (NEW 1/UPDATE 1) — {STAMP}"
BODY = f"출처 이슈: #139\n기준 CSV: old.csv\n생성 시각: {STAMP}"
CANDIDATE = f"dashboard/data/aisuit_{STAMP}.csv"


def record(no: int, sid: int, title: str) -> dict[str, str]:
    row = cs.empty_record()
    row.update({
        cs.COL_NO: str(no), cs.COL_SYSTEM_ID: str(sid), cs.COL_TITLE: title,
        cs.COL_PLAINTIFF: "Plaintiff", cs.COL_COUNTRY: "USA",
        cs.COL_HISTORY: "initial", cs.COL_LAST_UPDATE: "old",
    })
    return row


def proposal_files(tmp_path):
    base = cs.CanonicalCsv([cs.DEFAULT_TITLE], ["추출기간: test"], [record(1, 5000000001, "A v. B")])
    updated = dict(base.records[0])
    updated[cs.COL_STATUS] = "진행중"
    updated[cs.COL_LAST_UPDATE] = STAMP
    updated[cs.COL_HISTORY] += f"\n[{STAMP}] 진행현황 변경"
    new = record(2, 5000000002, "C v. D")
    new[cs.COL_HISTORY] = f"[{STAMP}] 등록: 신규 소송 추가"
    new[cs.COL_LAST_UPDATE] = STAMP
    candidate = cs.CanonicalCsv(base.title_row, base.period_row, [updated, new])
    base_path, candidate_path = tmp_path / "base.csv", tmp_path / "candidate.csv"
    cs.save(base, str(base_path)); cs.save(candidate, str(candidate_path))
    return base_path, candidate_path


def review(tmp_path, **overrides):
    base, candidate = proposal_files(tmp_path)
    args = dict(
        title=TITLE, body=BODY,
        changed_files=[{"filename": CANDIDATE, "status": "added"}],
        author="github-actions[bot]", head_ref=f"analyzer/{STAMP}",
    )
    args.update(overrides)
    return validate_proposal(str(base), str(candidate), **args)


def test_accepts_well_formed_proposal(tmp_path):
    result = review(tmp_path)
    assert result.accepted
    assert (result.new_count, result.update_count) == (1, 1)


def test_rejects_extra_file(tmp_path):
    result = review(tmp_path, changed_files=[
        {"filename": CANDIDATE, "status": "added"},
        {"filename": "analyzer/src/run.py", "status": "modified"},
    ])
    assert not result.accepted
    assert any("하나만" in reason for reason in result.reasons)


def test_rejects_untrusted_author(tmp_path):
    assert not review(tmp_path, author="some-fork").accepted


def test_rejects_count_mismatch(tmp_path):
    assert not review(tmp_path, title=TITLE.replace("UPDATE 1", "UPDATE 2")).accepted
