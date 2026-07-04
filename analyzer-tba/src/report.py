"""사람이 검토하기 쉬운 변경 요약(Markdown)을 만든다. PR 본문에 사용."""
from __future__ import annotations

from typing import Dict

from . import csv_store as cs


def changeset_markdown(changeset: Dict) -> str:
    s = changeset.get("summary", {})
    lines = [
        "## 🤖 Analyzer-TBA 변경 제안",
        "",
        f"- 출처 이슈: {changeset.get('source_issue', 'N/A')}",
        f"- 기준 CSV: `{changeset.get('base_csv', 'N/A')}`",
        f"- 생성 시각: {changeset.get('generated_at', 'N/A')}",
        f"- **신규(NEW): {s.get('new', 0)}건 / 업데이트(UPDATE): {s.get('update', 0)}건**",
        "",
        "> ✅ 이 PR을 **merge** 하면 변경이 정본 CSV에 반영됩니다(accept).",
        "> ❌ **close** 하면 반영되지 않습니다(reject).",
        "> 일부만 반영하려면 이 브랜치의 CSV를 직접 수정 후 커밋하세요.",
        "",
    ]

    news = [p for p in changeset.get("proposals", []) if p["type"] == "NEW"]
    ups = [p for p in changeset.get("proposals", []) if p["type"] == "UPDATE"]

    if news:
        lines += ["### 🆕 신규 소송", "", "| 신뢰도 | 소송제목 | 소송번호 | 제소일 | 피고 |", "|---|---|---|---|---|"]
        for p in news:
            r = p["record"]
            lines.append(
                f"| {p['confidence']:.2f} | {r.get(cs.COL_TITLE,'')} | "
                f"{r.get(cs.COL_DOCKET,'')} | {r.get(cs.COL_FILED,'')} | {r.get(cs.COL_DEFENDANT,'')} |"
            )
        lines.append("")

    if ups:
        lines += ["### ✏️ 업데이트", ""]
        for p in ups:
            lines.append(
                f"<details><summary><b>{p.get('match_key','')}</b> "
                f"(System ID {p.get('target_system_id','')}, 신뢰도 {p['confidence']:.2f}, "
                f"{len(p.get('field_changes', []))}개 필드)</summary>\n"
            )
            lines.append("| 컬럼 | 변경 전 | 변경 후 |")
            lines.append("|---|---|---|")
            for fc in p.get("field_changes", []):
                before = (fc["before"] or "∅").replace("\n", " ")[:80]
                after = (fc["after"] or "∅").replace("\n", " ")[:80]
                lines.append(f"| {fc['column']} | {before} | {after} |")
            lines.append("\n</details>\n")

    if not news and not ups:
        lines.append("_변경 제안이 없습니다 (모두 기존과 동일)._")
    return "\n".join(lines)
