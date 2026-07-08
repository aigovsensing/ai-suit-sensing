"""Analyzer 엔트리포인트 (CLI).

서브커맨드:
  analyze   이슈 수집→추출→대조→제안 생성. (검토 방식 A) 후보 CSV + PR 요약도 생성.
  review    CLI 대화형 검토(방식 B). changeset 의 decision 을 편집.
  apply     accept 된 제안을 정본 CSV 에 반영하여 새 버전 CSV 생성.

정본 CSV 는 analyze 단계에서 절대 변경하지 않는다.
"""
from __future__ import annotations

import argparse
import copy
import datetime as _dt
import json
import os
import sys

import yaml

# 패키지/단독 실행 모두 지원
try:
    from . import csv_store as cs
    from . import ingest, extract, matcher, changeset as csmod, apply as applymod, report
except ImportError:  # python src/run.py 로 직접 실행 시
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src import csv_store as cs
    from src import ingest, extract, matcher, changeset as csmod, apply as applymod, report

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # analyzer/


def _now_stamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d_%H%M")


def _now_iso() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _resolve(p: str) -> str:
    return p if os.path.isabs(p) else os.path.normpath(os.path.join(ROOT, p))


# ── analyze ────────────────────────────────────────────────────────────────
def cmd_analyze(args) -> int:
    cfg = load_config(args.config)
    data_dir = _resolve(cfg["data_dir"])
    proposals_dir = _resolve(cfg["proposals_dir"])
    os.makedirs(proposals_dir, exist_ok=True)

    base_path = args.base_csv or cs.latest_csv_path(data_dir)
    if not base_path:
        print(f"[!] 기준 CSV를 찾을 수 없습니다: {data_dir}", file=sys.stderr)
        return 2
    base = cs.load(base_path)
    print(f"[i] 기준 CSV: {base_path} ({len(base.records)}건)")

    # 0) 추출 결과 직접 주입 (테스트/재현용) — LLM/이슈 수집 생략
    if args.extracted_json:
        with open(args.extracted_json, encoding="utf-8") as f:
            extracted = json.load(f)
        source_issue = f"file://{args.extracted_json}"
        return _finish_analyze(cfg, base, base_path, extracted, source_issue, args)

    # 1) 이슈 텍스트 확보 (로컬 fixture 또는 GitHub)
    source_issue = "N/A"
    if args.issue_file:
        with open(args.issue_file, encoding="utf-8") as f:
            text = f.read()
        source_issue = f"file://{args.issue_file}"
        texts = [text]
    else:
        gh = cfg["github"]
        bundles = ingest.fetch_issues(
            gh["owner"], gh["repo"], gh["issue_label"],
            state=gh.get("issue_state", "all"), limit=args.limit,
        )
        if not bundles:
            print("[i] 분석할 이슈가 없습니다.")
            return 0
        source_issue = bundles[0].url
        texts = [b.full_text() for b in bundles]

    # 2) 추출
    extracted = []
    for t in texts:
        extracted.extend(
            extract.extract(t, llm_enabled=cfg["llm"]["enabled"], model=cfg["llm"]["model"])
        )
    return _finish_analyze(cfg, base, base_path, extracted, source_issue, args)


def _finish_analyze(cfg, base, base_path, extracted, source_issue, args) -> int:
    """추출 이후 단계: 대조 → 제안 생성 → (옵션) 후보 CSV."""
    data_dir = _resolve(cfg["data_dir"])
    proposals_dir = _resolve(cfg["proposals_dir"])
    print(f"[i] 추출된 소송 레코드: {len(extracted)}건")

    # 3) 대조
    results = matcher.classify(extracted, base, fuzzy_threshold=cfg["matching"]["fuzzy_threshold"])

    # 4) 제안 생성
    changeset = csmod.build_changeset(
        results, source_issue=source_issue, base_csv=base_path, generated_at=_now_iso()
    )
    stamp = _now_stamp()
    cs_path = os.path.join(proposals_dir, f"changeset_{stamp}.json")
    csmod.save_changeset(changeset, cs_path)
    md = report.changeset_markdown(changeset)
    md_path = os.path.join(proposals_dir, f"changeset_{stamp}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"[i] 제안: NEW {changeset['summary']['new']} / UPDATE {changeset['summary']['update']}")
    print(f"[✓] changeset: {cs_path}")
    print(f"[✓] 요약(MD):  {md_path}")

    # 5) (방식 A) 후보 CSV 생성: 모든 제안을 accepted 로 적용 → PR용
    has_changes = bool(changeset["summary"]["new"] or changeset["summary"]["update"])
    candidate_csv = ""
    if args.write_candidate and has_changes:
        candidate = copy.deepcopy(changeset)
        for p in candidate["proposals"]:
            p["decision"] = "accepted"
        new_base = applymod.apply_changeset(copy.deepcopy(base), candidate, stamp=stamp)[0]
        candidate_csv = cs.make_new_csv_name(data_dir, stamp)
        cs.save(new_base, candidate_csv)
        print(f"[✓] 후보 CSV: {candidate_csv}  → PR로 올려 검토(merge=accept/close=reject)")

    # 워크플로우(방식 A)가 읽을 산출물 경로/요약
    last_run = {
        "stamp": stamp,
        "has_changes": has_changes,
        "new": changeset["summary"]["new"],
        "update": changeset["summary"]["update"],
        "changeset": cs_path,
        "markdown": md_path,
        "candidate_csv": candidate_csv,
        "base_csv": base_path,
    }
    with open(os.path.join(proposals_dir, "last_run.json"), "w", encoding="utf-8") as f:
        json.dump(last_run, f, ensure_ascii=False, indent=2)
    return 0


# ── review (방식 B) ─────────────────────────────────────────────────────────
def cmd_review(args) -> int:
    changeset = csmod.load_changeset(args.changeset)
    for p in changeset["proposals"]:
        print("\n" + "=" * 60)
        print(f"[{p['type']}] id={p['id']} key={p['match_key']} conf={p['confidence']}")
        if p["type"] == "NEW":
            r = p["record"]
            print(f"  제목: {r.get(cs.COL_TITLE)}")
            print(f"  도켓: {r.get(cs.COL_DOCKET)} | 제소일: {r.get(cs.COL_FILED)}")
            print(f"  피고: {r.get(cs.COL_DEFENDANT)}")
        else:
            for fc in p.get("field_changes", []):
                print(f"  {fc['column']}: {fc['before'] or '∅'} → {fc['after']}")
        ans = input("  accept/reject/skip [a/r/s]? ").strip().lower()
        p["decision"] = {"a": "accepted", "r": "rejected"}.get(ans, "pending")
    csmod.save_changeset(changeset, args.changeset)
    print(f"\n[✓] 검토 결과 저장: {args.changeset}")
    return 0


# ── apply (방식 B) ──────────────────────────────────────────────────────────
def cmd_apply(args) -> int:
    cfg = load_config(args.config)
    data_dir = _resolve(cfg["data_dir"])
    changeset = csmod.load_changeset(args.changeset)
    base_path = changeset.get("base_csv") or cs.latest_csv_path(data_dir)
    base = cs.load(base_path)

    accepted = sum(1 for p in changeset["proposals"] if p.get("decision") == "accepted")
    if accepted == 0:
        print("[i] accept 된 제안이 없어 반영할 내용이 없습니다.")
        return 0

    stamp = _now_stamp()
    new_base, log = applymod.apply_changeset(base, changeset, stamp=stamp)
    out_csv = cs.make_new_csv_name(data_dir, stamp)
    cs.save(new_base, out_csv)
    print("\n".join(log))
    print(f"[✓] 반영 완료 ({accepted}건) → {out_csv}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="analyzer")
    ap.add_argument("--config", default=os.path.join(ROOT, "config.yaml"))
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze", help="이슈 분석 → 제안 생성 (+후보 CSV)")
    a.add_argument("--issue-file", help="로컬 이슈 텍스트 파일(테스트용)")
    a.add_argument("--extracted-json", help="추출 결과 JSON 직접 주입(LLM 생략, 테스트/재현용)")
    a.add_argument("--base-csv", help="기준 CSV 경로(기본: 최신)")
    a.add_argument("--limit", type=int, default=3, help="수집할 이슈 수")
    a.add_argument("--write-candidate", action="store_true", help="PR용 후보 CSV 생성")
    a.set_defaults(func=cmd_analyze)

    r = sub.add_parser("review", help="CLI 대화형 검토(방식 B)")
    r.add_argument("changeset", help="changeset json 경로")
    r.set_defaults(func=cmd_review)

    ap2 = sub.add_parser("apply", help="accept된 제안 반영(방식 B)")
    ap2.add_argument("changeset", help="changeset json 경로")
    ap2.set_defaults(func=cmd_apply)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
