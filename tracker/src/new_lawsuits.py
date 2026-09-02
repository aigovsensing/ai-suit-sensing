from __future__ import annotations
"""
신규 소송 제기 현황 (New Lawsuits) 모듈 — 리포트의 "3." 카테고리.

courtlistener.com 검색 결과에서 **Date Filed(소장 접수일)**를 기준으로, 최근
N일(LOOKBACK_DAYS) 이내에 '신규 접수'된 'AI 학습데이터 저작권' 관련 소송만
골라 마크다운 섹션으로 렌더링한다.

판단 기준(사용자 요구사항):
  - "Last Updated"가 아니라 **"Date Filed"** 값으로 신규 여부를 판단한다.
    예) Tanzer v. Adobe Inc. (3:26-cv-04712) → Date Filed: 2026-05-18 기준.
  - cutoff = 오늘(UTC) - lookback_days. dateFiled >= cutoff 인 건만 신규로 본다.

동작:
  - run.py 에서 이미 수행한 CourtListener 검색 결과(hits)를 재사용해 중복 호출을
    피한다. hits 가 None 이면 자체적으로 COURTLISTENER_QUERIES 를 질의한다.
  - 문서(type=r) 검색 결과 한 건에는 caseName/docketNumber/dateFiled/court/cause/
    docket_id/docket_absolute_url 등이 모두 들어 있어 추가 도켓 조회 없이 렌더링된다.
"""
import os
import html
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from typing import List, Optional

from .utils import debug_log
from .queries import COURTLISTENER_QUERIES
from .courtlistener import search_recent_documents, BASE
from .complaint_parse import dataset_url, extract_dataset_allegation, extract_dataset_names


def _md_escape(text: str) -> str:
    return (text or "").replace("[", "\\[").replace("]", "\\]")


def _court_str(hit: dict) -> str:
    """짧은 법원명(예: N.D. Cal.)을 우선 사용, 없으면 전체 명칭."""
    return (hit.get("court_citation_string") or hit.get("court") or "").strip()


def _nature_display(suit_nature: str) -> str:
    """
    Nature of Suit 값을 굵게(항상), '820 Copyright'이면 빨강색으로 표기.

    820 Copyright 는 저작권자의 허가 없이 데이터셋을 학습에 이용해 제기된
    'AI 학습데이터 저작권 소송'일 확률이 높아 눈에 띄게 강조한다.
    <b>/<span style>는 이메일(HTML)에서 굵게/빨강으로 렌더된다. GitHub은 style
    속성을 제거하므로, 820 인 경우 🔴 이모지로 시각적 강조를 보강한다.
    (참고: email_sender 의 인라인 스타일 패스가 <strong> 에 검정색을 강제하므로
     빨강 표기에는 <strong> 대신 <span style> 를 사용한다.)
    """
    val = (suit_nature or "").strip()
    if not val:
        return "미확인"
    safe = html.escape(val)
    if "820" in val:
        return f'<span style="color:#d32f2f;font-weight:700;">🔴 {safe}</span>'
    return f"<b>{safe}</b>"


def _resolve_lookback(lookback_days: Optional[int]) -> int:
    if lookback_days is not None:
        return lookback_days
    raw = (os.environ.get("LOOKBACK_DAYS") or "").strip()
    return int(raw) if raw.isdigit() and int(raw) > 0 else 6


def _related_datasets(hit: dict) -> str:
    """검색 결과의 소장 내용에서 데이터셋 이름과 관련 주장을 표시한다."""
    def display(name: str, url: str = "") -> str:
        """식별된 데이터셋을 리포트에서 눈에 띄는 빨간색으로 표시한다."""
        safe_name = html.escape(name)
        if url:
            safe_url = html.escape(url, quote=True)
            content = (
                f'<a href="{safe_url}" style="color:#d32f2f !important;">'
                f'{safe_name}</a>'
            )
        else:
            content = safe_name
        return f'<span style="color:#d32f2f;font-weight:700;">🔴 {content}</span>'

    text_fields = (
        hit.get("plain_text"), hit.get("snippet"), hit.get("text"),
        hit.get("description"), hit.get("short_description"),
        hit.get("extracted_ai_snippet"), hit.get("pdf_text_snippet"),
        hit.get("complaint_pdf_text"),
    )
    complaint_text = " ".join(str(value) for value in text_fields if value)
    names = extract_dataset_names(complaint_text)
    rendered = {
        name.casefold(): display(name, dataset_url(name) or "")
        for name in names
    }

    # 호출자가 구조화한 데이터셋 정보를 제공하는 경우에도 이를 빠뜨리지 않는다.
    supplied = hit.get("related_datasets") or []
    if isinstance(supplied, str):
        supplied = [supplied]
    for dataset in supplied:
        if isinstance(dataset, dict):
            name = str(dataset.get("name") or "").strip()
            url = str(dataset.get("url") or "").strip()
            value = display(name, url)
        else:
            name = str(dataset).strip()
            value = display(name)
        if name:
            # 구조화 데이터는 URL 등 더 풍부한 정보를 가질 수 있으므로 같은 이름을
            # 소장 텍스트에서 이미 찾았더라도 해당 표시로 교체한다.
            rendered[name.casefold()] = value
            if not any(existing.casefold() == name.casefold() for existing in names):
                names.append(name)

    if not rendered:
        return "확인되지 않음"

    allegation = extract_dataset_allegation(complaint_text, names, max_len=220)
    datasets = ", ".join(rendered.values())
    return f"{datasets} — 소장문서 관련 주장: {allegation}" if allegation else datasets


def build_new_lawsuits_section(
    report_date: Optional[str] = None,
    lookback_days: Optional[int] = None,
    hits: Optional[List[dict]] = None,
) -> str:
    """
    '신규 소송 제기 현황' 마크다운 섹션(## 3.)을 생성한다.

    Args:
        report_date: 표기용 날짜(YYYY-MM-DD). 미지정 시 KST 오늘.
        lookback_days: 신규 판단 기간(일). 미지정 시 env LOOKBACK_DAYS(기본 6).
        hits: 재사용할 CourtListener 검색 결과. None 이면 자체 질의.
    """
    try:
        lookback_days = _resolve_lookback(lookback_days)
        today = report_date or datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")

        # 1) 검색 결과 확보 (run.py 결과 재사용 or 자체 질의)
        if hits is None:
            hits = []
            for q in COURTLISTENER_QUERIES:
                try:
                    hits.extend(search_recent_documents(q, days=lookback_days, max_results=20))
                except Exception as e:
                    debug_log(f"[new_lawsuits] 검색 실패({q[:40]}...): {e}")

        # 2) Date Filed 기준으로 '신규' 필터 + 도켓 단위 중복 제거
        cutoff = datetime.now(timezone.utc).date() - timedelta(days=lookback_days)
        by_key: dict = {}
        for h in hits or []:
            date_val = (h.get("dateFiled") or h.get("date_filed") or "")[:10]
            if not date_val:
                continue
            try:
                dt = datetime.fromisoformat(date_val).date()
            except Exception:
                continue
            if dt < cutoff:
                continue  # Date Filed 가 기간 밖 → 신규 아님
            key = h.get("docket_id") or (h.get("caseName"), h.get("docketNumber"))
            prev = by_key.get(key)
            if prev is None or date_val > prev.get("_date_filed", ""):
                item = dict(h)
                item["_date_filed"] = date_val
                by_key[key] = item

        cases = sorted(by_key.values(), key=lambda x: x["_date_filed"], reverse=True)

        header = "## 3. 신규 소송 제기 현황 (출처: courtlistener.com)"
        intro = (
            f"> courtlistener.com에서 **Date Filed(소장 접수일) 기준 최근 {lookback_days}일 이내** "
            "신규 접수된 'AI 학습데이터 저작권' 관련 소송입니다. (참고: 'Last Updated'가 아니라 "
            "'Date Filed' 값으로 신규 여부를 판단합니다.)"
        )

        if not cases:
            return f"{header}\n\n{intro}\n\n_최근 {lookback_days}일 이내 신규 접수된 소송이 없습니다._"

        lines: List[str] = [header, "", intro, "", f"* **총 {len(cases)}건**", ""]
        for i, c in enumerate(cases, 1):
            name = (c.get("caseName") or "미확인").strip()
            docket_no = (c.get("docketNumber") or "").strip()
            date_filed = c["_date_filed"]
            court = _court_str(c)
            suit_nature = (c.get("suitNature") or "").strip()
            cause = (c.get("cause") or "").strip()
            rel = c.get("docket_absolute_url") or ""
            url = (BASE + rel) if rel.startswith("/") else rel

            title = f"{name} ({docket_no})" if docket_no else name
            link = f"[{_md_escape(title)}]({url})" if url else f"**{_md_escape(title)}**"

            first = f"Date Filed: {date_filed}"
            if court:
                first += f" | 법원: {court}"

            lines.append(f"{i}. {link}")
            lines.append(f"   - {first}")
            lines.append(f"   - Nature of Suit: {_nature_display(suit_nature)}")
            if cause:
                lines.append(f"   - Cause: {cause}")
            lines.append(f"   - 관련 데이터셋: {_related_datasets(c)}")

        return "\n".join(lines)
    except Exception as e:
        debug_log(f"[new_lawsuits] '신규 소송 제기 현황' 생성 실패: {e}")
        return ""
