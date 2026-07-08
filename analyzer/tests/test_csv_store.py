"""csv_store round-trip / 식별 헬퍼 테스트.

실행: analyzer/ 에서  python -m tests.test_csv_store
(외부 의존성 없이 표준 라이브러리만 사용)
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import csv_store as cs  # noqa: E402

REAL_CSV = os.path.join(
    os.path.dirname(__file__), "..", "..", "dashboard", "data", "aisuit_20260624_0947.csv"
)


def test_load_real_csv():
    obj = cs.load(REAL_CSV)
    assert len(obj.records) == 180, f"유효 레코드 180건 기대, 실제 {len(obj.records)}"
    assert obj.max_no() == 180
    first = obj.records[0]
    assert first[cs.COL_TITLE] == "S.A. JAMENDO v. NVIDIA"
    assert first[cs.COL_DOCKET] == "5:26-cv-06206"
    print("[ok] load_real_csv: 180 records")


def test_docket_index_and_normalize():
    obj = cs.load(REAL_CSV)
    idx = obj.by_docket()
    assert cs.normalize_docket(" 5:26-CV-06206 ") == "5:26-cv-06206"
    assert "5:26-cv-06206" in idx
    print("[ok] docket index + normalize")


def test_roundtrip_preserves_records():
    obj = cs.load(REAL_CSV)
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "aisuit_test.csv")
        cs.save(obj, out)
        reloaded = cs.load(out)
    assert len(reloaded.records) == len(obj.records)
    # 모든 컬럼 값이 보존되는지 (멀티라인 셀 포함)
    for a, b in zip(obj.records, reloaded.records):
        assert a == b, f"round-trip 불일치: {a.get(cs.COL_NO)}"
    assert reloaded.title_row[0] == obj.title_row[0]
    assert reloaded.period_row[0] == obj.period_row[0]
    print("[ok] roundtrip preserves all records & metadata")


def test_append_record():
    obj = cs.load(REAL_CSV)
    n0 = len(obj.records)
    rec = obj.append_record({cs.COL_TITLE: "Foo v. Bar", cs.COL_DOCKET: "1:26-cv-99999"})
    assert rec[cs.COL_NO] == "181"
    assert len(obj.records) == n0 + 1
    print("[ok] append_record assigns No=181")


if __name__ == "__main__":
    test_load_real_csv()
    test_docket_index_and_normalize()
    test_roundtrip_preserves_records()
    test_append_record()
    print("\nALL TESTS PASSED ✅")
