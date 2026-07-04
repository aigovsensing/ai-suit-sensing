"""matcher → changeset → apply 핵심 파이프라인 테스트 (네트워크/LLM 불필요).

실행: analyzer-tba/ 에서  python -m tests.test_pipeline
"""
import copy
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import csv_store as cs  # noqa: E402
from src import matcher, changeset as csmod, apply as applymod  # noqa: E402

REAL_CSV = os.path.join(
    os.path.dirname(__file__), "..", "..", "dashboard", "data", "aisuit_20260624_0947.csv"
)


def _extracted():
    return [
        # UPDATE: 기존 NVIDIA 건의 진행현황 변경
        {
            cs.COL_TITLE: "S.A. JAMENDO v. NVIDIA",
            cs.COL_DOCKET: "5:26-cv-06206",
            cs.COL_STATUS: "진행중",
            cs.COL_RESULT: "약식판결 신청 기각",
        },
        # NEW: 신규 소송
        {
            cs.COL_TITLE: "Foo Authors v. Bar AI",
            cs.COL_DOCKET: "1:26-cv-99999",
            cs.COL_FILED: "2026-06-24",
            cs.COL_DEFENDANT: "Bar AI",
            cs.COL_STATUS: "소 제기됨",
        },
        # UNCHANGED: 기존 건과 동일(빈 값만) → 제안 제외
        {
            cs.COL_TITLE: "Shakespeare et al. v. Anthropic et al.",
            cs.COL_DOCKET: "3:26-cv-05931",
        },
    ]


def test_classify():
    base = cs.load(REAL_CSV)
    results = matcher.classify(_extracted(), base, fuzzy_threshold=88)
    types = sorted(r.type for r in results)
    assert types == ["NEW", "UNCHANGED", "UPDATE"], types
    upd = next(r for r in results if r.type == "UPDATE")
    cols = {c.column for c in upd.field_changes}
    assert cs.COL_STATUS in cols and cs.COL_RESULT in cols
    print("[ok] classify → NEW/UPDATE/UNCHANGED")


def test_changeset_excludes_unchanged():
    base = cs.load(REAL_CSV)
    results = matcher.classify(_extracted(), base)
    ch = csmod.build_changeset(results, source_issue="test", base_csv=REAL_CSV, generated_at="now")
    assert ch["summary"] == {"new": 1, "update": 1}, ch["summary"]
    assert all(p["decision"] == "pending" for p in ch["proposals"])
    print("[ok] changeset summary new=1 update=1, all pending")


def test_apply_accepted_only():
    base = cs.load(REAL_CSV)
    results = matcher.classify(_extracted(), base)
    ch = csmod.build_changeset(results, source_issue="test", base_csv=REAL_CSV, generated_at="now")

    # pending 상태로 apply → 아무것도 반영 안 됨
    none_applied, log0 = applymod.apply_changeset(copy.deepcopy(base), ch, stamp="20260624_1600")
    assert len(none_applied.records) == 180, "pending은 반영되면 안 됨"

    # 모두 accept → 반영
    for p in ch["proposals"]:
        p["decision"] = "accepted"
    applied, log = applymod.apply_changeset(copy.deepcopy(base), ch, stamp="20260624_1600")
    assert len(applied.records) == 181, f"NEW 1건 추가 기대, {len(applied.records)}"

    # NVIDIA 건 UPDATE 검증
    nvidia = applied.by_docket()["5:26-cv-06206"]
    assert nvidia[cs.COL_STATUS] == "진행중"
    assert nvidia[cs.COL_RESULT] == "약식판결 신청 기각"
    assert nvidia[cs.COL_LAST_UPDATE] == "20260624_1600"
    assert "소 제기됨 → 진행중" in nvidia[cs.COL_HISTORY]

    # 신규 건 검증
    foo = applied.by_docket()["1:26-cv-99999"]
    assert foo[cs.COL_NO] == "181"
    print("[ok] apply: accepted만 반영, NEW=181 + UPDATE 히스토리 누적")


def test_save_roundtrip_after_apply():
    base = cs.load(REAL_CSV)
    results = matcher.classify(_extracted(), base)
    ch = csmod.build_changeset(results, source_issue="t", base_csv=REAL_CSV, generated_at="now")
    for p in ch["proposals"]:
        p["decision"] = "accepted"
    applied, _ = applymod.apply_changeset(copy.deepcopy(base), ch, stamp="20260624_1600")
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "aisuit_20260624_1600.csv")
        cs.save(applied, out)
        reloaded = cs.load(out)
    assert len(reloaded.records) == 181
    assert reloaded.by_docket()["5:26-cv-06206"][cs.COL_STATUS] == "진행중"
    print("[ok] apply 결과 저장 후 재로드 정합성")


if __name__ == "__main__":
    test_classify()
    test_changeset_excludes_unchanged()
    test_apply_accepted_only()
    test_save_roundtrip_after_apply()
    print("\nALL PIPELINE TESTS PASSED ✅")
