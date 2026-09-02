from __future__ import annotations
"""
소송사건에 연관된 데이터셋 현황 (Dataset Status) 모듈.

조간/석간/통합 리포트의 **제일 마지막**에 붙는 섹션을 생성한다.
저작권자 허가 없이 AI 학습에 사용되어 분쟁 대상이 된 '데이터셋'을 한데 모아,
연구논문·제품 양산에 해당 데이터셋을 사용하지 않도록 참고할 수 있게 한다.

데이터셋 식별은 complaint_parse.extract_dataset_names(공개 텍스트 기반 자동 추출)를
재사용하며, 다음 두 입력을 지원한다:
  - build_dataset_status_section_from_hits(hits): CourtListener 검색 결과(구조화된
    소송 dict 목록)에서 소송별 데이터셋을 집계 → 데이터셋별 '연관 소송' 목록 제공.
  - build_dataset_status_section_from_text(text): 이미 조립된 리포트/댓글 텍스트에서
    데이터셋 이름만 추출 → 목록으로 제공(연관 소송 개별 매핑은 생략).
"""
import html
from typing import Dict, List, Optional

from .complaint_parse import extract_dataset_names, dataset_url

# CourtListener 루트(도켓 상대경로 → 절대 URL 변환용). courtlistener.BASE 와 동일하나,
# 무거운 import 체인(pypdf 등)을 피하려 여기서 상수로 둔다.
BASE = "https://www.courtlistener.com"

DEFAULT_HEADER = "## 🧬 소송사건에 연관된 데이터셋 현황"

_INTRO = (
    "> 아래는 위 소송사건들의 소장·기사에서 **명시적으로 식별된 데이터셋**입니다. "
    "저작권자 허가 없이 AI 학습에 사용되어 분쟁 대상이 된 데이터셋일 수 있으므로, "
    "**연구논문·제품 양산에 사용하기 전 라이선스·적법성을 반드시 확인**하세요."
)
_GUIDANCE = (
    "> ⚠️ 식별은 공개 텍스트 기반 자동 추출이라 누락·오탐이 있을 수 있고, 표기된 "
    "데이터셋이라도 사건별로 쟁점·판단이 다릅니다. 개별 소송 내용을 함께 확인하세요."
)


def _cell(text: str) -> str:
    """마크다운 표 셀용 이스케이프(파이프/개행 제거)."""
    return (str(text or "")).replace("|", "\\|").replace("\n", " ").strip()


def _dataset_badge(name: str) -> str:
    """식별된 데이터셋을 눈에 띄는 빨간색으로 표기(이메일=빨강, GitHub=🔴)."""
    return f'<span style="color:#d32f2f;font-weight:700;">🔴 {html.escape(name)}</span>'


def _case_text(hit: dict) -> str:
    fields = (
        hit.get("plain_text"), hit.get("snippet"), hit.get("text"),
        hit.get("description"), hit.get("short_description"),
        hit.get("extracted_ai_snippet"), hit.get("pdf_text_snippet"),
        hit.get("complaint_pdf_text"),
    )
    return " ".join(str(v) for v in fields if v)


def _names_for_hit(hit: dict) -> List[str]:
    names = extract_dataset_names(_case_text(hit))
    supplied = hit.get("related_datasets") or []
    if isinstance(supplied, str):
        supplied = [supplied]
    for d in supplied:
        nm = (d.get("name") if isinstance(d, dict) else d)
        nm = str(nm or "").strip()
        if nm and not any(nm.casefold() == x.casefold() for x in names):
            names.append(nm)
    return names


def enrich_hits_with_complaint_documents(
    hits: Optional[List[dict]], documents: Optional[List[object]]
) -> List[dict]:
    """PDF에서 추출한 소장 본문을 같은 도켓의 검색 결과에 결합한다.

    CourtListener 검색 결과에는 소장 PDF 본문이 없는 경우가 많다. 이후 단계가 실제
    소장 내용을 기준으로 데이터셋을 판별할 수 있도록 도켓 ID가 같은 문서의 추출
    텍스트를 별도 필드에 보존한다. 원본 hit 객체는 변경하지 않는다.
    """
    text_by_docket: Dict[object, List[str]] = {}
    for document in documents or []:
        docket_id = getattr(document, "docket_id", None)
        text = str(getattr(document, "pdf_text_snippet", "") or "").strip()
        if docket_id is not None and text:
            text_by_docket.setdefault(docket_id, []).append(text)

    enriched = []
    matched_dockets = set()
    for hit in hits or []:
        item = dict(hit)
        docket_id = hit.get("docket_id")
        texts = text_by_docket.get(docket_id, [])
        if texts:
            item["complaint_pdf_text"] = " ".join(dict.fromkeys(texts))
            matched_dockets.add(docket_id)
        enriched.append(item)

    # 뉴스의 도켓번호로 추가 조회한 소장은 최초 검색 hits에 없을 수 있다. 이 문서도
    # 데이터셋 현황에서 빠지지 않도록 최소한의 hit 형태로 변환한다.
    for document in documents or []:
        docket_id = getattr(document, "docket_id", None)
        text = str(getattr(document, "pdf_text_snippet", "") or "").strip()
        if docket_id is None or not text or docket_id in matched_dockets:
            continue
        enriched.append({
            "docket_id": docket_id,
            "caseName": getattr(document, "case_name", "") or "미확인",
            "docketNumber": getattr(document, "docket_number", "") or "",
            "dateFiled": getattr(document, "date_filed", "") or "",
            "complaint_pdf_text": " ".join(dict.fromkeys(text_by_docket[docket_id])),
        })
        matched_dockets.add(docket_id)
    return enriched


def _aggregate_from_hits(hits: Optional[List[dict]]) -> Dict[str, dict]:
    """데이터셋(casefold) -> {'name', 'cases': [(case_name, url), ...]} 집계."""
    agg: Dict[str, dict] = {}
    seen_dockets = set()
    for h in hits or []:
        key = h.get("docket_id") or (h.get("caseName"), h.get("docketNumber"))
        if key in seen_dockets:
            continue
        seen_dockets.add(key)

        names = _names_for_hit(h)
        if not names:
            continue

        case_name = (h.get("caseName") or "미확인").strip()
        rel = h.get("docket_absolute_url") or ""
        curl = (BASE + rel) if isinstance(rel, str) and rel.startswith("/") else rel
        for nm in names:
            slot = agg.setdefault(nm.casefold(), {"name": nm, "cases": []})
            if not any(cn == case_name for cn, _ in slot["cases"]):
                slot["cases"].append((case_name, curl))
    return agg


def _render(agg: Dict[str, dict], header: str, show_cases: bool) -> str:
    if not agg:
        return (
            f"{header}\n\n{_INTRO}\n\n"
            "_이번 리포트에서 명시적으로 식별된 데이터셋은 없습니다._"
        )

    rows = sorted(agg.values(), key=lambda s: (-len(s.get("cases") or []), s["name"].lower()))
    lines: List[str] = [header, "", _INTRO, "", f"* **식별된 데이터셋: {len(rows)}종**", ""]

    if show_cases:
        lines.append("| 데이터셋 | 연관 소송 수 | 공식 링크 | 연관 소송 |")
        lines.append("|---|---|---|---|")
        for s in rows:
            url = dataset_url(s["name"])
            link = f"[🔗 원본]({url})" if url else "-"
            cases = s.get("cases") or []
            n = len(cases)
            if cases:
                shown = "<br>".join(
                    (f"[{_cell(cn)}]({cu})" if cu else _cell(cn)) for cn, cu in cases[:5]
                )
                if n > 5:
                    shown += f"<br>… 외 {n - 5}건"
            else:
                shown = "-"
            lines.append(f"| {_dataset_badge(s['name'])} | {n or '-'} | {link} | {shown} |")
    else:
        lines.append("| 데이터셋 | 공식 링크 |")
        lines.append("|---|---|")
        for s in rows:
            url = dataset_url(s["name"])
            link = f"[🔗 원본]({url})" if url else "-"
            lines.append(f"| {_dataset_badge(s['name'])} | {link} |")

    lines.append("")
    lines.append(_GUIDANCE)
    return "\n".join(lines)


def build_dataset_status_section_from_hits(
    hits: Optional[List[dict]], header: str = DEFAULT_HEADER
) -> str:
    """CourtListener 검색 결과(hits)에서 데이터셋별 연관 소송을 집계해 섹션을 만든다."""
    try:
        return _render(_aggregate_from_hits(hits), header, show_cases=True)
    except Exception:
        # 리포트 전체를 깨뜨리지 않도록 안전 폴백(빈 섹션 생략)
        return ""


def build_dataset_status_section_from_text(
    text: str, header: str = DEFAULT_HEADER
) -> str:
    """이미 조립된 리포트/댓글 텍스트에서 데이터셋 이름만 추출해 섹션을 만든다."""
    try:
        names = extract_dataset_names(text or "")
        agg: Dict[str, dict] = {}
        for nm in names:
            agg.setdefault(nm.casefold(), {"name": nm, "cases": []})
        return _render(agg, header, show_cases=False)
    except Exception:
        return ""


def build_dataset_status_section(
    hits: Optional[List[dict]], text: str, header: str = DEFAULT_HEADER
) -> str:
    """구조화 검색 결과와 조립된 리포트 텍스트를 함께 사용해 누락을 줄인다.

    CourtListener 검색 스니펫은 짧아서 데이터셋 명칭이 잘리는 경우가 많다. 따라서
    소송별 매핑은 ``hits``에서 유지하되, 기사 및 Gemini 요약에 명시된 이름도 최종
    목록에 합친다. 텍스트에서만 확인된 이름은 연관 소송 수를 추정하지 않는다.
    """
    try:
        agg = _aggregate_from_hits(hits)
        for name in extract_dataset_names(text or ""):
            agg.setdefault(name.casefold(), {"name": name, "cases": []})
        return _render(agg, header, show_cases=True)
    except Exception:
        return ""
