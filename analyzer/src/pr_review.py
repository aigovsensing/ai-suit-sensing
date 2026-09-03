"""Automated, deterministic review of analyzer dataset pull requests.

The GitHub entry point intentionally downloads blobs through the API instead of
checking out untrusted pull-request code.  Validation is kept separate so it can
be exercised locally and in unit tests.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import csv_store as cs


TITLE_RE = re.compile(
    r"^(?:🤖\s*)?소송 데이터 갱신 제안 \(NEW (\d+)/UPDATE (\d+)\) — (\d{8}_\d{4})(?:\s*-\s*#?\d+)?$"
)
DATA_RE = re.compile(r"^dashboard/data/aisuit_(\d{8}(?:_\d{4})?)\.csv$")
ALLOWED_AUTHORS = {"github-actions[bot]", "aigovsensing"}
REQUIRED_NEW_FIELDS = (cs.COL_TITLE, cs.COL_PLAINTIFF, cs.COL_COUNTRY)


@dataclass
class ReviewResult:
    accepted: bool
    reasons: list[str] = field(default_factory=list)
    new_count: int = 0
    update_count: int = 0
    stamp: str = ""

    def markdown(self) -> str:
        icon, verdict = ("✅", "ACCEPT / MERGE") if self.accepted else ("❌", "REJECT / CLOSE")
        checks = "\n".join(f"- {reason}" for reason in self.reasons) or "- 검증 항목 없음"
        return (
            f"## {icon} 자동 리뷰: {verdict}\n\n{checks}\n\n"
            f"- 검증 결과: NEW {self.new_count} / UPDATE {self.update_count}\n"
            f"- 기준 시각: `{self.stamp or 'N/A'}`\n\n"
            "> 이 판정은 정본 보존·스키마·건수·출처 추적성을 기계적으로 검증한 결과입니다."
        )


def _fail(result: ReviewResult, message: str) -> None:
    result.accepted = False
    result.reasons.append(f"❌ {message}")


def validate_proposal(
    base_path: str,
    candidate_path: str,
    *,
    title: str,
    body: str,
    changed_files: list[dict[str, Any]],
    author: str,
    head_ref: str,
) -> ReviewResult:
    """Return an accept/reject decision; malformed input is always rejected."""
    result = ReviewResult(accepted=True)
    match = TITLE_RE.fullmatch(title.strip())
    if not match:
        _fail(result, "PR 제목이 약속된 형식과 다릅니다.")
        expected_new = expected_update = -1
    else:
        expected_new, expected_update, result.stamp = int(match[1]), int(match[2]), match[3]

    if author not in ALLOWED_AUTHORS:
        _fail(result, f"허용되지 않은 PR 작성자입니다: `{author}`")
    if not head_ref.startswith("analyzer/"):
        _fail(result, f"분석기 브랜치가 아닙니다: `{head_ref}`")

    added = [f for f in changed_files if f.get("status") == "added"]
    candidate_name = added[0].get("filename", "") if len(added) == 1 else ""
    if len(changed_files) != 1 or len(added) != 1 or not DATA_RE.fullmatch(candidate_name):
        _fail(result, "PR은 새 정본 CSV 파일 하나만 추가해야 합니다.")
    filename_match = DATA_RE.fullmatch(candidate_name)
    if not filename_match or (result.stamp and filename_match[1] != result.stamp):
        _fail(result, "CSV 파일명의 타임스탬프가 PR 제목과 일치하지 않습니다.")
    if result.stamp and any(label not in body for label in ("출처 이슈:", "기준 CSV:", "생성 시각:")):
        _fail(result, "PR 본문에 출처 이슈·기준 CSV·생성 시각 추적 정보가 부족합니다.")

    try:
        base, candidate = cs.load(base_path), cs.load(candidate_path)
    except (OSError, ValueError) as exc:
        _fail(result, f"CSV 파싱/스키마 검증 실패: `{exc}`")
        return result

    base_by_id = {r[cs.COL_SYSTEM_ID]: r for r in base.records}
    cand_by_id = {r[cs.COL_SYSTEM_ID]: r for r in candidate.records}
    if len(cand_by_id) != len(candidate.records):
        _fail(result, "System ID가 중복됩니다.")
    removed = set(base_by_id) - set(cand_by_id)
    if removed:
        _fail(result, f"기존 레코드 {len(removed)}건이 삭제됐습니다.")

    new_ids = set(cand_by_id) - set(base_by_id)
    result.new_count = len(new_ids)
    history_marker = f"[{result.stamp}]" if result.stamp else ""
    update_count = 0
    for sid, old in base_by_id.items():
        new = cand_by_id.get(sid)
        if not new:
            continue
        if old[cs.COL_NO] != new[cs.COL_NO]:
            _fail(result, f"System ID {sid}의 No가 변경됐습니다.")
        if not new[cs.COL_HISTORY].startswith(old[cs.COL_HISTORY]):
            _fail(result, f"System ID {sid}의 히스토리가 삭제/개작됐습니다.")
        changed = any(old[c] != new[c] for c in cs.COLUMNS)
        additions = new[cs.COL_HISTORY].count(history_marker) - old[cs.COL_HISTORY].count(history_marker) if history_marker else 0
        if changed:
            if additions <= 0:
                _fail(result, f"System ID {sid} 변경의 히스토리 감사 기록이 없습니다.")
            if new[cs.COL_LAST_UPDATE] != result.stamp:
                _fail(result, f"System ID {sid}의 Last Update가 제안 시각과 다릅니다.")
            update_count += max(additions, 0)
    result.update_count = update_count

    expected_nos = list(range(base.max_no() + 1, base.max_no() + len(new_ids) + 1))
    actual_nos: list[int] = []
    for sid in new_ids:
        row = cand_by_id[sid]
        if not row[cs.COL_NO].isdigit():
            _fail(result, f"신규 System ID {sid}의 No가 숫자가 아닙니다.")
        else:
            actual_nos.append(int(row[cs.COL_NO]))
        missing = [c for c in REQUIRED_NEW_FIELDS if not row[c].strip()]
        if missing:
            _fail(result, f"신규 System ID {sid}의 필수값이 비었습니다: {', '.join(missing)}")
        if history_marker and history_marker not in row[cs.COL_HISTORY]:
            _fail(result, f"신규 System ID {sid}에 등록 히스토리가 없습니다.")
    if sorted(actual_nos) != expected_nos:
        _fail(result, "신규 No가 기존 번호 뒤에 중복 없이 연속해야 합니다.")

    if result.new_count != expected_new or result.update_count != expected_update:
        _fail(
            result,
            f"제목 건수(NEW {expected_new}/UPDATE {expected_update})와 CSV "
            f"검증 건수(NEW {result.new_count}/UPDATE {result.update_count})가 다릅니다.",
        )
    if result.accepted:
        result.reasons.extend([
            "✅ 작성자·브랜치·단일 CSV 변경 정책 통과",
            "✅ 23개 정본 컬럼 스키마와 System ID/No 무결성 통과",
            "✅ 기존 레코드 보존과 히스토리 append-only 규칙 통과",
            "✅ PR 표기 건수와 실제 NEW/UPDATE 건수 일치",
        ])
    return result


class GitHub:
    def __init__(self, repo: str, token: str):
        self.root = f"https://api.github.com/repos/{repo}"
        self.token = token

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(self.root + path, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                raw = response.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"GitHub API {method} {path}: {exc.code} {exc.read().decode()}") from exc

    def blob(self, sha: str) -> bytes:
        data = self.request("GET", f"/git/blobs/{sha}")
        return base64.b64decode(data["content"])


def review_github_pr(event_path: str, repo: str, token: str) -> ReviewResult:
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    pr = event["pull_request"]
    number = pr["number"]
    gh = GitHub(repo, token)
    files = gh.request("GET", f"/pulls/{number}/files?per_page=100")
    candidates = [f for f in files if DATA_RE.fullmatch(f["filename"]) and f["status"] == "added"]

    # Find the latest canonical CSV in the trusted base commit tree.
    tree = gh.request("GET", f"/git/trees/{pr['base']['sha']}?recursive=1")["tree"]
    bases = sorted(x for x in tree if DATA_RE.fullmatch(x["path"]) and x["type"] == "blob")
    with tempfile.TemporaryDirectory() as tmp:
        base_path = Path(tmp, "base.csv")
        candidate_path = Path(tmp, "candidate.csv")
        if bases:
            base_path.write_bytes(gh.blob(bases[-1]["sha"]))
        if candidates:
            candidate_path.write_bytes(gh.blob(candidates[0]["sha"]))
        result = validate_proposal(
            str(base_path), str(candidate_path), title=pr["title"], body=pr.get("body") or "",
            changed_files=files,
            author=pr["user"]["login"], head_ref=pr["head"]["ref"],
        )

    gh.request("POST", f"/issues/{number}/comments", {"body": result.markdown()})
    if result.accepted:
        gh.request("PUT", f"/pulls/{number}/merge", {
            "merge_method": "merge", "sha": pr["head"]["sha"],
            "commit_title": f"data: auto-accept lawsuit dataset proposal #{number}",
        })
    else:
        gh.request("PATCH", f"/pulls/{number}", {"state": "closed"})
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", default=os.getenv("GITHUB_EVENT_PATH"))
    parser.add_argument("--repo", default=os.getenv("GITHUB_REPOSITORY"))
    args = parser.parse_args()
    token = os.getenv("GITHUB_TOKEN", "")
    if not args.event or not args.repo or not token:
        parser.error("--event, --repo and GITHUB_TOKEN are required")
    result = review_github_pr(args.event, args.repo, token)
    print(result.markdown())
    return 0 if result.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
