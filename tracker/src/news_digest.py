from __future__ import annotations
"""
당일 뉴스 소식 (Daily News Digest) 모듈.

조간/석간 뉴스 이메일·GitHub 이슈에 함께 실리는 "당일 뉴스 소식" 섹션을 생성한다.

동작 방식 (AI 미사용, 순수 구글 뉴스 검색/RSS 기반 — Google Alert 유사):
  1) 구글 뉴스 RSS 검색으로 최근 N일간의 'AI 학습데이터 저작권 소송' 관련 기사를 수집.
  2) 기사 제목을 정규화하여 '중복(유사) 기사'끼리 군집화(cluster)한다.
     같은 사건을 여러 매체가 보도할수록 군집 크기가 커지며, 이는 곧 화제성(hot)을 의미.
  3) 국내(한글 제목) / 해외(외신) 2개 구분으로 나눈 뒤, 각 구분에서 중복 건수가
     많은 순으로 정렬하여 상위 5개를 노출한다.
  4) 5위 밖의 기사는 "더보기 (N개)" 접기(<details>) 안에 담아, 원할 때만 펼쳐 보게 한다.

이 섹션은 마크다운으로 생성되며, GitHub 이슈 댓글과 (email_sender 의 마크다운→HTML
변환을 거쳐) 이메일 본문에 그대로 렌더링된다.
"""
import os
import re
import html
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
from zoneinfo import ZoneInfo

import feedparser

from .utils import debug_log, parse_dt

# ─────────────────────────────────────────────────────────────
# 설정
# ─────────────────────────────────────────────────────────────
# 상위 몇 개까지 펼쳐 보여줄지 (나머지는 "더보기"로 접힘)
TOP_N = 5
# 유사 제목으로 묶는 자카드(Jaccard) 임계값 (0~1). 높을수록 엄격.
_SIM_THRESHOLD = 0.5

# 구글 뉴스 RSS 검색 엔드포인트
_GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={gl}:{lang}"

# 국내(한국어) 검색 쿼리
_KO_QUERIES = [
    "AI 학습데이터 저작권 소송",
    "생성형 AI 저작권 침해 판결",
    "AI 저작권 소송",
]
# 해외(영문) 검색 쿼리
_EN_QUERIES = [
    '"AI training data" (copyright OR lawsuit OR ruling)',
    '(Suno OR Anthropic OR OpenAI OR Meta) copyright (AI OR "training data")',
    '"AI copyright" (lawsuit OR sued OR court OR ruling)',
]

_HANGUL_RE = re.compile(r"[가-힣]")


@dataclass
class _Article:
    title: str          # 매체명 접미사를 제거한 순수 헤드라인
    raw_title: str      # 원본(매체명 포함)
    url: str
    source: str
    published_at: datetime | None


@dataclass
class _Cluster:
    """유사(중복) 기사 군집. 크기가 클수록 화제성이 높다."""
    articles: List[_Article] = field(default_factory=list)
    tokens: set = field(default_factory=set)

    @property
    def count(self) -> int:
        return len(self.articles)

    @property
    def rep(self) -> _Article:
        """대표 기사: 가장 최신 기사를 대표로 사용."""
        return max(
            self.articles,
            key=lambda a: a.published_at or datetime(1970, 1, 1, tzinfo=timezone.utc),
        )


# ─────────────────────────────────────────────────────────────
# 수집
# ─────────────────────────────────────────────────────────────
def _strip_source_suffix(title: str) -> str:
    """구글 뉴스 제목은 'Headline - 매체명' 형식 → 매체명 접미사 제거."""
    parts = title.rsplit(" - ", 1)
    if len(parts) == 2 and 0 < len(parts[1]) <= 40:
        return parts[0].strip()
    return title.strip()


def _fetch(queries: List[str], hl: str, gl: str, lang: str, lookback_days: int) -> List[_Article]:
    items: List[_Article] = []
    seen: set[str] = set()
    for q in queries:
        query = f"{q} when:{lookback_days}d"
        feed_url = _GOOGLE_NEWS_RSS.format(
            q=query.replace(" ", "%20"), hl=hl, gl=gl, lang=lang
        )
        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            debug_log(f"[news_digest] RSS 파싱 실패 ({q}): {e}")
            continue
        debug_log(f"[news_digest] '{q}' → {len(feed.entries)}건")
        for e in feed.entries:
            raw_title = (getattr(e, "title", "") or "").strip()
            link = (getattr(e, "link", "") or "").strip()
            if not raw_title or not link or link in seen:
                continue
            seen.add(link)
            source = ""
            if hasattr(e, "source") and e.source:
                source = getattr(e.source, "title", "") or ""
            items.append(
                _Article(
                    title=_strip_source_suffix(raw_title),
                    raw_title=raw_title,
                    url=link,
                    source=source,
                    published_at=parse_dt(getattr(e, "published", None)),
                )
            )
    return items


# ─────────────────────────────────────────────────────────────
# 군집화 (중복 기사 묶기)
# ─────────────────────────────────────────────────────────────
def _tokenize(title: str) -> set:
    t = title.lower()
    # 한글/영문/숫자만 남기고 토큰화
    t = re.sub(r"[^0-9a-z가-힣]+", " ", t)
    return {w for w in t.split() if len(w) > 1}


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _cluster(articles: List[_Article]) -> List[_Cluster]:
    clusters: List[_Cluster] = []
    for art in articles:
        tokens = _tokenize(art.title)
        if not tokens:
            continue
        best: _Cluster | None = None
        best_score = 0.0
        for c in clusters:
            score = _jaccard(tokens, c.tokens)
            if score > best_score:
                best_score = score
                best = c
        if best is not None and best_score >= _SIM_THRESHOLD:
            best.articles.append(art)
            best.tokens |= tokens
        else:
            clusters.append(_Cluster(articles=[art], tokens=set(tokens)))
    # 중복 건수(내림차순) → 최신순 정렬
    clusters.sort(
        key=lambda c: (
            c.count,
            c.rep.published_at or datetime(1970, 1, 1, tzinfo=timezone.utc),
        ),
        reverse=True,
    )
    return clusters


# ─────────────────────────────────────────────────────────────
# 렌더링 (마크다운)
# ─────────────────────────────────────────────────────────────
def _md_escape(text: str) -> str:
    return text.replace("[", "\\[").replace("]", "\\]")


def _render_category(header: str, clusters: List[_Cluster]) -> str:
    lines: List[str] = [f"### {header}"]
    if not clusters:
        lines.append("")
        lines.append("_최근 관련 기사가 없습니다._")
        lines.append("")
        return "\n".join(lines)

    lines.append("")
    top = clusters[:TOP_N]
    rest = clusters[TOP_N:]

    for i, c in enumerate(top, 1):
        rep = c.rep
        badge = f" 🔥 (중복 {c.count}건)" if c.count > 1 else ""
        lines.append(f"{i}. [{_md_escape(rep.title)}]({rep.url}){badge}")

    if rest:
        # 5위 밖은 "더보기 (N개)" 접기 안에 노출 (GitHub·이메일 공통 렌더)
        rest_total = sum(c.count for c in rest)
        items_html = "\n".join(
            f'  <li><a href="{html.escape(c.rep.url, quote=True)}">'
            f"{html.escape(c.rep.title)}</a>"
            + (f" 🔥 (중복 {c.count}건)" if c.count > 1 else "")
            + "</li>"
            for c in rest
        )
        lines.append("")
        lines.append("<details>")
        lines.append(f"<summary>더보기 ({len(rest)}개)</summary>")
        lines.append("")
        lines.append("<ul>")
        lines.append(items_html)
        lines.append("</ul>")
        lines.append("</details>")
        _ = rest_total  # (참고용) 접힌 기사들의 총 중복 건수

    lines.append("")
    return "\n".join(lines)


def build_daily_news_section(report_date: str | None = None, lookback_days: int | None = None) -> str:
    """
    '당일 뉴스 소식' 마크다운 섹션을 생성한다. 실패하거나 기사가 전혀 없으면 "" 반환.

    Args:
        report_date: 표기용 날짜 (YYYY-MM-DD). 미지정 시 KST 오늘.
        lookback_days: 검색 기간(일). 미지정 시 env DAILY_NEWS_LOOKBACK_DAYS(기본 2).
    """
    try:
        if lookback_days is None:
            raw = (os.environ.get("DAILY_NEWS_LOOKBACK_DAYS") or "").strip()
            lookback_days = int(raw) if raw.isdigit() and int(raw) > 0 else 2

        today = report_date or datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")

        ko_items = _fetch(_KO_QUERIES, "ko", "KR", "ko", lookback_days)
        en_items = _fetch(_EN_QUERIES, "en-US", "US", "en", lookback_days)

        # url 기준 전역 중복 제거 후, 제목의 한글 포함 여부로 국내/해외 분류
        merged: dict[str, _Article] = {}
        for art in ko_items + en_items:
            merged.setdefault(art.url, art)

        domestic: List[_Article] = []
        overseas: List[_Article] = []
        for art in merged.values():
            if _HANGUL_RE.search(art.title):
                domestic.append(art)
            else:
                overseas.append(art)

        dom_clusters = _cluster(domestic)
        ovs_clusters = _cluster(overseas)

        if not dom_clusters and not ovs_clusters:
            debug_log("[news_digest] 수집된 기사가 없어 '당일 뉴스 소식' 섹션을 생략합니다.")
            return ""

        parts: List[str] = [
            f"## 📰 당일 뉴스 소식 ({today})",
            "",
            f"> 최근 {lookback_days}일간 구글 뉴스에서 수집한 'AI 학습데이터 저작권 소송' "
            "관련 기사입니다. **중복 보도(유사 제목) 건수가 많을수록 화제성이 높은** 순서로 정렬했습니다.",
            "",
            _render_category("(국내) AI 학습데이터 저작권 소송", dom_clusters),
            _render_category("(해외) AI 학습데이터 저작권 소송", ovs_clusters),
        ]
        return "\n".join(parts).strip()
    except Exception as e:
        debug_log(f"[news_digest] '당일 뉴스 소식' 생성 실패: {e}")
        return ""
