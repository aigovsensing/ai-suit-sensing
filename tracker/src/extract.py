from __future__ import annotations
import re
import requests
import yaml
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from .utils import debug_log, parse_dt
import json

CASE_NO_PATTERNS = [
    re.compile(r"\b\d:\d{2}-cv-\d{5}\b", re.IGNORECASE),
    re.compile(r"\b\d{1,2}:\d{2}-cv-\d{5}\b", re.IGNORECASE),
    re.compile(r"\b\d{4}-cv-\d{4,6}\b", re.IGNORECASE),
]

@dataclass
class Lawsuit:
    update_or_filed_date: str
    # case_title: 가능한 경우 "A v. B" 형태의 사건명(소송제목)
    case_title: str
    # article_title: RSS/기사 원문 제목(기사제목)
    article_title: str
    case_number: str
    reason: str
    article_urls: List[str]


def fetch_page_text(url: str, timeout: int = 15) -> tuple[str, str, BeautifulSoup | None]:
    """기사 페이지 텍스트를 가져오고 (텍스트, 최종URL, soup)을 반환한다.

    - Google News RSS 링크는 최종 매체 URL로 리다이렉트되는 경우가 많아,
      allow_redirects=True로 최종 URL을 확보해 기사 주소 출력/후속 분석 정확도를 높인다.
    - 네트워크/차단 등의 이유로 실패할 수 있으므로 예외는 삼키고 빈 값 반환.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        r = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
        r.raise_for_status()
        final_url = (r.url or url).strip()
        soup = BeautifulSoup(r.text, "lxml")
        
        # 텍스트 추출용 복사본 (원본 soup은 날짜 추출 등에 사용 위해 보존)
        soup_copy = BeautifulSoup(r.text, "lxml")
        for tag in soup_copy(["script", "style", "noscript"]):
            tag.decompose()
        text = soup_copy.get_text("\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text[:20000], final_url, soup
    except Exception as e:
        debug_log(f"fetch_page_text failed: {url}, error: {e}")
        return "", url, None

def extract_publication_date(soup: BeautifulSoup | None, text: str = "", url: str = "") -> datetime | None:
    """HTML의 메타 태그나 JSON-LD, URL, 본문 텍스트 등에서 기사 발행일을 추출합니다."""
    if not soup:
        return None
    
    found_dates: List[datetime] = []

    # 1. Open Graph / Article meta tags
    # article:published_time, published_at, date, etc.
    properties = [
        "article:published_time", "og:article:published_time", "og:published_time",
        "publication_date", "publish-date", "publish_date",
        "dc.date", "dc.date.issued", "date", "pubdate",
        "sailthru.date", "parsely-pub-date", "bt:pubDate",
        "article:published", "published_time", "release_date",
        "last-modified", "last_modified", "og:updated_time", "article:modified_time"
    ]
    for prop in properties:
        meta = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        if meta and meta.get("content"):
            dt = parse_dt(meta["content"])
            if dt: found_dates.append(dt)

    # 2. JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            def find_dates_in_json(obj):
                if isinstance(obj, dict):
                    # datePublished가 가장 정확하며, dateCreated를 차선책으로 활용
                    for k in ["datePublished", "dateCreated", "dateModified", "pubDate"]:
                        if k in obj and obj[k]:
                            dt = parse_dt(str(obj[k]))
                            if dt: found_dates.append(dt)
                    for v in obj.values():
                        find_dates_in_json(v)
                elif isinstance(obj, list):
                    for item in obj:
                        find_dates_in_json(item)
            
            find_dates_in_json(data)
        except Exception:
            continue

    # 3. <time> tag
    for time_tag in soup.find_all("time"):
        if time_tag.get("datetime"):
            dt = parse_dt(time_tag["datetime"])
            if dt: found_dates.append(dt)
        elif time_tag.get_text():
            dt = parse_dt(time_tag.get_text().strip())
            if dt: found_dates.append(dt)
    
    # 4. URL에서 날짜 추출 (예: /2024/05/20/...)
    if url:
        url_date_match = re.search(r"/(\d{4})/(\d{1,2})/(\d{1,2})/", url)
        if url_date_match:
            try:
                dt = datetime(int(url_date_match.group(1)), int(url_date_match.group(2)), int(url_date_match.group(3)), tzinfo=timezone.utc)
                found_dates.append(dt)
            except ValueError:
                pass

    # 5. 본문 텍스트에서 날짜 추출 (regex fallback)
    if text:
        # "October 7, 2025" or "Oct 7, 2025" 패턴 (영어 기사 위주)
        month_pat = r"(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        date_regex = re.compile(month_pat + r"\s+\d{1,2},?\s+\d{4}", re.IGNORECASE)
        # 상위 2000자 내에서만 탐색
        for m in date_regex.finditer(text[:2000]):
            dt = parse_dt(m.group(0))
            if dt: found_dates.append(dt)

    if found_dates:
        # 발견된 날짜 중 미래의 날짜나 너무 과거(2000년 이전)는 제외
        now = datetime.now(timezone.utc)
        valid_dates = [d for d in found_dates if 2000 < d.year <= now.year + 1 and d < now + timedelta(days=2)]
        if valid_dates:
            # 기사 발행일은 보통 발견된 날짜 중 가장 이른 날짜일 가능성이 높음 (Update된 날짜가 섞일 수 있으므로)
            # 단, meta tag나 JSON-LD에서 나온 날짜가 있으면 그것을 더 신뢰해야 함.
            # 여기서는 단순하게 가장 작은(과거) 날짜를 선택하여 '최초 발행일'에 가깝게 추정.
            best_date = min(valid_dates)
            return best_date
    
    return None

def load_known_cases(path: str = "data/known_cases.yml") -> List[Dict[str, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or []
    except FileNotFoundError:
        return []

def enrich_from_known(text: str, title: str, known: List[Dict[str, Any]]) -> Dict[str, str]:
    hay = (title + "\n" + text).lower()
    for entry in known:
        any_terms = [t.lower() for t in entry.get("match", {}).get("any", [])]
        if any_terms and any(term in hay for term in any_terms):
            return entry.get("enrich", {}) or {}
    return {}

def extract_case_number(text: str) -> str:
    for pat in CASE_NO_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(0)
    return "미확인"

def extract_case_title_from_text(text: str) -> str:
    """본문 텍스트에서 'A v. B' 형태의 사건명을 최대한 추출한다.

    기사 제목이 사건명이 아닌 경우가 많아, 본문에서 사건명을 찾는 것이 훨씬 정확하다.
    예: "The New York Times v. OpenAI" / "Authors v. Anthropic" 등.

    오탐을 줄이기 위해:
    - 너무 짧은 캡션/문장 제외
    - 후보가 여러 개면 길이/키워드 점수로 최적 1개 선택
    """
    t = (text or "")[:20000]
    if not t:
        return "미확인"

    # 흔한 변형: v, v., vs, vs.
    pat = re.compile(
        r"([A-Z][A-Za-z0-9 ,.&'\-]{2,}?)\s+v\.?s?\.?\s+([A-Z][A-Za-z0-9 ,.&'\-]{2,}?)\b"
    )
    cands = []
    for m in pat.finditer(t):
        a = m.group(1).strip(" ,.;:-")
        b = m.group(2).strip(" ,.;:-")
        # 너무 긴 문자열/광고 문구 등 제외
        if len(a) < 3 or len(b) < 3:
            continue
        if len(a) > 80 or len(b) > 80:
            continue
        cand = f"{a} v. {b}"
        cands.append(cand)

    if not cands:
        return "미확인"

    # 간단 스코어링: 'et al' / 'Inc' / 'LLC' / 'PBC' 등 법률 문맥 가점
    def score(x: str) -> float:
        xl = x.lower()
        bonus = 0.0
        for kw in ["et al", "inc", "llc", "ltd", "pbc", "corp", "company", "microsoft", "openai", "anthropic", "google", "meta", "nvidia", "amazon", "times"]:
            if kw in xl:
                bonus += 0.2
        # 너무 짧으면 감점
        base = min(len(x) / 40.0, 2.0)
        return base + bonus

    best = max(cands, key=score)
    return best


def guess_case_title_from_article_title(title: str) -> str:
    """기사 제목에서 사건명(소송제목)을 최대한 추정한다.

    - 가장 신뢰하는 형태: "A v. B" / "A vs. B" / "A v B"
    - 그 외: "... v. ..."가 없으면 미확인
    """
    t = (title or "").strip()
    if not t:
        return "미확인"

    # 흔한 기사 접미사(" - 매체명" 등) 제거
    t = re.sub(r"\s+[-|–|—]\s+[^-–—|]{2,}$", "", t).strip()

    # A v. B 패턴
    m = re.search(r"([A-Z][A-Za-z0-9 ,.&'\-]{2,})\s+v\.?s?\.?\s+([A-Z][A-Za-z0-9 ,.&'\-]{2,})", t)
    if m:
        return f"{m.group(1).strip()} v. {m.group(2).strip()}"

    return "미확인"

def reason_heuristic(hay: str) -> str:
    h = hay.lower()
    # 1. 특정 서비스/플랫폼/데이터 기반
    if "shadow library" in h or "pirat" in h or "books3" in h:
        return "불법 유통본/해적판(Books3 등) 등으로 추정되는 데이터셋을 AI 모델 학습에 활용한 것에 따른 저작권 침해 주장."
    if "youtube" in h:
        return "유튜브 콘텐츠를 무단 수집(Scraping)하여 AI 학습에 사용하고, 서비스 약관 및 기술적 보호조치를 위반했다는 주장."
    if "lyrics" in h or "music publisher" in h or "musical works" in h:
        return "저작물인 음악 가사 및 곡 정보를 무단으로 학습에 사용하여 권리자의 저작권을 침해했다는 주장."
    if "news" in h and ("publisher" in h or "journalism" in h):
        return "언론사의 기사 콘텐츠를 데이터 학습에 무단 활용하여 저작권 및 상업적 가치를 훼손했다는 주장."
    if "artist" in h and ("style" in h or "artwork" in h):
        return "예술가의 작품을 무단 학습하여 스타일을 모방하거나 저작권을 부당하게 이용했다는 주장."
    if "trade secret" in h or "confidential" in h:
        return "기업의 영업비밀에 해당하는 데이터를 무단 취득하여 AI 모델 개발 등에 활용했다는 의혹."
    if any(k in h for k in ["contract", "licensing", "agreement", "partnership", "계약", "협력", "제휴"]):
        return "AI 학습용 데이터 공급 계약 또는 제휴 협력과 관련된 소식이며, 권리 관계 및 계약 조건 등이 주요 쟁점입니다."

    # 2. 일반적인 AI 학습 관련 (Keywords based)
    if any(k in h for k in ["training data", "ai training", "model training"]):
        return "AI 모델 학습을 위해 허가되지 않은 데이터를 대량으로 수집하여 저작권 및 관련 법규를 위반했다는 취지의 소송."

    return "AI 모델 학습 및 서비스 개발 과정에서의 무단 데이터 수집 및 저작권 침해 관련 분쟁."

def build_lawsuits_from_news(news_items, known_cases, lookback_days: int = 3) -> List[Lawsuit]:
    results: List[Lawsuit] = []
    debug_log(f"build_lawsuits_from_news items={len(news_items)} lookback={lookback_days}")
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    for item in news_items:
        if item.published_at and item.published_at < cutoff:
            continue
        text, final_url, soup = fetch_page_text(item.url)
        if not text:
            continue

        hay = (item.title + " " + text)
        lower = hay.lower()
        if not any(k in lower for k in ["lawsuit", "sued", "litigation", "copyright", "dmca", "pirat", "unauthoriz", "training data", "dataset"]):
            debug_log(f"Skipped non-relevant news: {item.title[:60]}...")
            continue

        enrich = enrich_from_known(text, item.title, known_cases)

        # 1) 본문에서 소송번호/사건명 추출 (가장 정확)
        case_number = enrich.get("case_number") or extract_case_number(text)
        article_title = item.title
        case_title = enrich.get("case_title") or extract_case_title_from_text(text)
        if case_title == "미확인":
            case_title = guess_case_title_from_article_title(article_title)

        # 2) 날짜 처리: 웹페이지에서 추출한 날짜 우선, 없으면 RSS 날짜 사용
        web_date = extract_publication_date(soup, text=text, url=final_url)
        if web_date:
            published = web_date
            debug_log(f"Using web extracted date: {published} for {article_title[:40]}")
        else:
            published = item.published_at or datetime.now(timezone.utc)
        
        update_date = published.date().isoformat()

        results.append(
            Lawsuit(
                update_or_filed_date=update_date,
                case_title=case_title,
                article_title=article_title,
                case_number=case_number,
                reason=enrich.get("reason", reason_heuristic(hay)),
                article_urls=sorted(list({final_url, item.url})),
            )
        )

    # 병합
    merged: Dict[tuple[str, str, str], Lawsuit] = {}
    for r in results:
        # 사건번호가 없는 경우도 있어 (case_number, case_title, article_title)로 최대한 보존
        key = (r.case_number, r.case_title, r.article_title)
        if key not in merged:
            merged[key] = r
        else:
            merged[key].article_urls = sorted(list(set(merged[key].article_urls + r.article_urls)))
            if r.update_or_filed_date > merged[key].update_or_filed_date:
                merged[key].update_or_filed_date = r.update_or_filed_date

    return list(merged.values())