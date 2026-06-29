from __future__ import annotations
from typing import List
from collections import Counter
import re
import copy
from datetime import datetime
from .extract import Lawsuit
from .courtlistener import CLDocument, CLCaseSummary
from .utils import debug_log, slugify_case_name

def _esc(s: str) -> str:
    s = str(s or "").strip()
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = s.replace("```", "&#96;&#96;&#96;")
    s = s.replace("~~~", "&#126;&#126;&#126;")
    s = s.replace("|", "\\|")
    s = s.replace("\n", "<br>")
    return s


def _md_sep(col_count: int) -> str:
    return "|" + "---|" * col_count


def _get_data_icon(text: str) -> str:
    """
    대상 데이터/정보의 성격에 따른 적정 아이콘(이미지 배지)을 반환합니다.
    분류: Authors/Books, Music/Recordings, Video/Film, Visual Art, News, Publishers, Voice/Likeness, Code/Software, Other
    """
    h = (text or "").lower()
    
    # 1. Authors/Books
    if any(k in h for k in ["book", "novel", "author", "writing", "literary", "library", "shadow library", "pirat", "books3", "prose"]):
        return "📚 ![Authors/Books](https://img.shields.io/badge/Authors%2FBooks-4b2e83?style=flat-square)"
    
    # 2. Music/Recordings
    if any(k in h for k in ["music", "lyrics", "audio", "song", "musical", "singer", "artist", "record", "spotify", "warner", "sony", "universal"]):
        return "🎵 ![Music/Recordings](https://img.shields.io/badge/Music%2FRecordings-1DB954?style=flat-square)"
    
    # 3. Video/Film
    if any(k in h for k in ["video", "youtube", "movie", "film", "netflix", "vimeo", "motion picture"]):
        return "🎥 ![Video/Film](https://img.shields.io/badge/Video%2FFilm-E50914?style=flat-square)"
    
    # 4. Visual Art
    if any(k in h for k in ["image", "photo", "picture", "art", "style", "drawing", "illustration", "artwork", "photographer", "getty", "deviantart", "midjourney", "stable diffusion", "stock"]):
        return "🖼️ ![Visual Art](https://img.shields.io/badge/Visual%20Art-005A9C?style=flat-square)"
        
    # 5. News
    if any(k in h for k in ["news", "article", "journalism", "times", "newspaper", "press", "reporting"]):
        return "📰 ![News](https://img.shields.io/badge/News-fcc200?style=flat-square&logoColor=black)"

    # 6. Publishers
    if any(k in h for k in ["publisher", "proquest", "elsevier", "springer", "wiley", "academic", "journal", "media"]):
        return "🏢 ![Publishers](https://img.shields.io/badge/Publishers-0077B5?style=flat-square)"

    # 7. Voice/Likeness
    if any(k in h for k in ["voice", "likeness", "personality", "biometric", "avatar", "deepfake", "speech", "vocal", "name and likeness"]):
        return "🗣️ ![Voice/Likeness](https://img.shields.io/badge/Voice%2FLikeness-FF6F61?style=flat-square)"

    # 8. Code/Software
    if any(k in h for k in ["code", "software", "programming", "github", "source code", "developer", "copilot", "git"]):
        return "💻 ![Code/Software](https://img.shields.io/badge/Code%2FSoftware-24292e?style=flat-square)"

    # 9. Other (Fallback)
    return "📁 ![Other](https://img.shields.io/badge/Other-grey?style=flat-square)"


def _mdlink(label: str, url: str) -> str:
    label = _esc(label)
    url = (url or "").strip()
    if not url:
        return label

    # 이미 Markdown 링크 형식이면 그대로 반환 (이중 방지)
    if url.startswith("[") and "](" in url:
        return url
        
    return f"[{label}]({url})"


def _short(val: str, limit: int = 140) -> str:
    val = val or ""
    if len(val) <= limit:
        return _esc(val)
    return f"<details><summary>내용 펼치기</summary>{_esc(val)}</details>"


# =====================================================
# slug 변환
# =====================================================
def _slugify_case_name(name: str) -> str:
    return slugify_case_name(name)


# =====================================================
# 비인가 데이터 학습 소송 감지 기준 정의
# =====================================================
DETECTION_CRITERIA = [
    ("무단 데이터 수집 명시", ["scrape", "crawl", "ingest", "harvest", "mining", "extraction", "bulk", "collection", "robots.txt", "common crawl", "laion", "the pile", "bookcorpus", "unauthorized"], 25),
    ("모델 학습 직접 언급", ["train", "training", "model", "llm", "generative ai", "genai", "gpt", "transformer", "weight", "fine-tune", "diffusion", "inference"], 20),
    ("저작권 직접 언급", ["820", "3820", "copyright"], 30),
    ("저작권 관련/쟁점", ["infringement", "dmca", "fair use", "derivative", "exclusive"], 10),
    ("상업적 사용", ["commercial", "profit", "monetiz", "revenue", "subscription", "enterprise", "paid", "for-profit"], 10),
    ("집단소송", ["class action", "putative class", "representative"], 5),
    ("데이터 제공 계약/협력", ["contract", "licensing", "agreement", "partnership", "계약", "협력", "제휴"], -10),
]


# =====================================================
# 뉴스 감지 레벨
# =====================================================
def calculate_news_detection_score(title: str, reason: str) -> tuple[int, List[str]]:
    score = 0
    matched_keywords = []
    text = f"{title or ''} {reason or ''}".lower()

    for name, keywords, points in DETECTION_CRITERIA:
        found = [k for k in keywords if k in text]
        if found:
            score += points
            # 각 카테고리에서 발견된 첫 2개 키워드만 표시 (너무 길어짐 방지)
            matched_keywords.append(f"{name}: {', '.join(found[:2])}")

    # [핵심] 저작권 + 모델 학습 동시 감지 시 가점 (+50)
    if any(k in text for k in ["820", "3820", "copyright"]) and any(k in text for k in ["train", "training"]):
        score += 50
        matched_keywords.insert(0, "핵심: 저작권 소송 내 모델 학습 직접 언급 (Critical)")

    return max(0, min(score, 100)), matched_keywords


def format_detection_level(score: int) -> str:
    if score >= 80:
        return f"🔥 {score}"
    if score >= 60:
        return f"⚠️ {score}"
    if score >= 40:
        return f"🟡 {score}"
    return f"🟢 {score}"


# =====================================================
# RECAP 감지 레벨
# =====================================================
def calculate_case_detection_score(case: CLCaseSummary) -> int:
    score = 0
    text = f"{case.extracted_ai_snippet or ''} {case.extracted_causes or ''}".lower()
    nature = (case.nature_of_suit or "").lower()

    # 0. 핵심 AI 학습 저작권 소송 (+50)
    # 820 Copyright 이면서 소장 내 train 키워드 발견 시 (Critical Priority)
    if ("820" in nature or "copyright" in nature) and any(k in text for k in ["train", "training"]):
        score += 50

    # 1. 무단 데이터 수집 명시 (+25)
    if any(k in text for k in ["scrape", "crawl", "ingest", "harvest", "mining", "extraction", "bulk", "collection", "robots.txt", "common crawl", "laion", "the pile", "bookcorpus", "unauthorized"]):
        score += 25
    
    # 2. 모델 학습 직접 언급 (+20)
    if any(k in text for k in ["train", "training", "model", "llm", "generative ai", "genai", "gpt", "transformer", "weight", "fine-tune", "diffusion", "inference"]):
        score += 20
    
    # 3. 저작권 직접 언급 (+30)
    # NOS 코드 820, 3820 또는 copyright 키워드
    if "820" in nature or "3820" in nature or any(k in text for k in ["820", "3820", "copyright"]):
        score += 30

    # 4. 저작권 관련/쟁점 (+10)
    if any(k in text for k in ["infringement", "dmca", "fair use", "derivative", "exclusive"]):
        score += 10

    # 5. 상업적 사용 (+10)
    if any(k in text for k in ["commercial", "profit", "monetiz", "revenue", "subscription", "enterprise", "paid", "for-profit"]):
        score += 10
        
    # 6. 집단소송 (+5)
    if any(k in text for k in ["class action", "putative class", "representative"]):
        score += 5

    # 7. 데이터 제공 계약/협력 (-10)
    if any(k in text for k in ["contract", "licensing", "agreement", "partnership", "계약", "협력", "제휴"]):
        score -= 10

    return max(0, min(score, 100))


# =====================================================
# 메인 렌더
# =====================================================
def render_markdown(
    lawsuits: List[Lawsuit],
    cl_docs: List[CLDocument],
    cl_cases: List[CLCaseSummary],
    recap_doc_count: int,
    lookback_days: int = 3,
) -> str:

    lines: List[str] = []

    # KPI (간결 텍스트 요약)
    lines.append("<details>")
    lines.append(f"<summary><strong>## 📊 최근 {lookback_days}일 소송 동향 요약</strong></summary>")
    lines.append("")
    lines.append(f"└ 📰 News: {len(lawsuits)}")
    lines.append(f"└ ⚖ Cases: {len(cl_cases)} (Docs: {recap_doc_count})")
    lines.append("</details>\n")

    # Nature 통계
    if cl_cases:
        counter = Counter([c.nature_of_suit or "미확인" for c in cl_cases])
        lines.append("<details>")
        lines.append("<summary><strong>## 📊 Nature of Suit 통계</strong></summary>")
        lines.append("")
        lines.append("| Nature of Suit | 건수 |")
        lines.append("|---|---|")
        for k, v in counter.most_common(10):
            lines.append(f"| {_esc(k)} | **{v}** |")
        # 총 개수 추가
        total_count = sum(counter.values())
        lines.append(f"| **총개수** | **{total_count}** |")            
        lines.append("</details>\n")

    # Target Data 통계 (신규 추가)
    if cl_cases or lawsuits:
        data_categories = []
        for c in cl_cases:
            data_categories.append(_get_data_category(f"{c.case_name} {c.nature_of_suit} {c.cause} {c.extracted_causes} {c.extracted_ai_snippet}"))
        for s in lawsuits:
            data_categories.append(_get_data_category(f"{s.article_title} {s.case_title} {s.reason}"))
            
        category_counter = Counter(data_categories)
        lines.append("<details>")
        lines.append("<summary><strong>## 📊 Target Data (학습 데이터) 통계</strong></summary>")
        lines.append("")
        lines.append("| Item | 건수 |")
        lines.append("|---|---|")
        # 사용자가 제시한 항목 순서 또는 건수 순으로 출력
        for k, v in category_counter.most_common():
            lines.append(f"| {k} | **{v}** |")
        lines.append(f"| **총개수** | **{sum(category_counter.values())}** |")
        lines.append("</details>\n")

    # AI 소송 Top3 (업데이트 날짜 기준)
    if cl_cases:
        # 820 Copyright 항목들만 필터링 (820, 저작권, Copyright 키워드 포함 시)
        copyright_cases = []
        for c in cl_cases:
            nos = str(c.nature_of_suit or "").strip()
            if "820" in nos or "copyright" in nos.lower():
                copyright_cases.append(c)
        
        top_cases = sorted(
            copyright_cases,
            key=lambda x: x.recent_updates if x.recent_updates != "미확인" else "",
            reverse=True
        )[:3]

        if top_cases:
            debug_log(f"Rendering Top 3 Copyright cases: {len(top_cases)} found")
            lines.append("<details>")
            lines.append("<summary><strong>## 🧠 최근 \"820 Copyright\" 소송 Top 3 (업데이트 날짜 기준)</strong></summary>")
            lines.append("")
            
            for idx, c in enumerate(top_cases, start=1):
                update_date = c.recent_updates if c.recent_updates != "미확인" else ""
                
                # CourtListener 링크 생성
                slug = _slugify_case_name(c.case_name)
                docket_url = f"https://www.courtlistener.com/docket/{c.docket_id}/{slug}/"
                
                # 데이터 성격에 따른 아이콘 결정
                icon = _get_data_icon(f"{c.case_name} {c.nature_of_suit} {c.cause} {c.extracted_causes} {c.extracted_ai_snippet}")
                
                full_title = f"{icon} ({idx}) {update_date or '미확인'}, {c.case_name}"
                lines.append(f"**{_mdlink(full_title, docket_url)}**")
                
                # Nature (820 Copyright 강조)
                nature_val = str(c.nature_of_suit or "미확인").strip()
                if "820" in nature_val:
                    nature_display = f"⚠️**{_esc(nature_val)}**"
                else:
                    nature_display = _esc(nature_val)
                
                lines.append(f"   - **Nature**: {nature_display}")
                lines.append(f"   - **도켓번호**: {_esc(c.docket_number or '미확인')}")
                lines.append(f"   - **소송이유**: {_esc(c.extracted_causes or c.cause or '미확인')}")
                
                # AI학습관련 핵심주장 (Snippet)
                if c.extracted_ai_snippet:
                    lines.append(f"   - **AI학습관련 핵심주장**: {_short(c.extracted_ai_snippet, 200)}")
                else:
                    lines.append(f"   - **AI학습관련 핵심주장**: 미확인")
                lines.append("")
            lines.append("</details>\n")
        else:
            debug_log("No 820 Copyright cases found for Top 3 section.")

    # 뉴스 테이블
    lines.append("### 📰 AI Suit News")
    if lawsuits:
        debug_log("'News' is printed.")
        lines.append("")
        lines.append("> ℹ️ **중복건수** 표기: `제`=제목 완전일치, `키`=키워드(BM25) 유사, `의`=의미론적 유사 (예: `8 (제:6 키:2 의:0)`)")
        lines.append("")
        lines.append("| No. | 기사일자 | 제목 | 소송번호 | 조건 (주요 키워드) | 소송사유 | 감지 레벨⬇️ | 중복건수 |")
        lines.append(_md_sep(8))

        # 기사일자 기준으로 정렬 (날짜 내림차순, 동일 날짜 시 감지 레벨 내림차순)
        scored_lawsuits = []
        for s in lawsuits:
            risk_score, keywords = calculate_news_detection_score(s.article_title or s.case_title, s.reason)
            scored_lawsuits.append((risk_score, keywords, s))
        
        scored_lawsuits.sort(key=lambda x: (x[0], x[2].update_or_filed_date or ""), reverse=True)

        for idx, (risk_score, keywords, s) in enumerate(scored_lawsuits, start=1):
            article_url = s.article_urls[0] if getattr(s, "article_urls", None) else ""
            # 데이터 성격에 따른 아이콘 결정
            icon = _get_data_icon(f"{s.article_title} {s.case_title} {s.reason}")
            title_cell = f"{icon} " + _mdlink(s.article_title or s.case_title, article_url)

            keyword_display = "<br>".join(keywords) if keywords else "-"

            lines.append(
                f"| {idx} | "
                f"{_esc(s.update_or_filed_date)} | "
                f"{title_cell} | "
                f"{_esc(s.case_number)} | "
                f"{_esc(keyword_display)} | "
                f"{_short(s.reason)} | "
                f"{format_detection_level(risk_score)} | "
                f"0 |"
            )
        lines.append("")
    else:
        lines.append("새로운 소식이 0건입니다.\n")

    # RECAP 케이스
    lines.append("### ⚖️ Cases (Courtlistener+RECAP)")
    if cl_cases:
        
        # CLDocument를 docket_id 기준으로 매핑
        doc_map = {}
        for d in cl_docs:
            if d.docket_id:
                doc_map[d.docket_id] = d
        
        lines.append("")
        lines.append(
            "| No. | 상태 | 케이스명 | 도켓번호 | Nature | 감지 레벨⬇️ | "
            "소송이유 | AI학습관련 핵심주장 | 법적 근거 | 담당판사 | 법원 | "
            "Complaint 문서 번호 | Complaint PDF 링크 | 최근 도켓 업데이트 |"
        )
        lines.append(_md_sep(14))
        
        # 감지 레벨 점수 기준으로 정렬 (내림차순, 동일 점수 시 날짜 내림차순)
        scored_cases = []
        for c in cl_cases:
            # 최종 스코어링 소스 텍스트 결정
            ext_causes = c.extracted_causes
            ext_snippet = c.extracted_ai_snippet
            if c.docket_id in doc_map:
                doc = doc_map[c.docket_id]
                ext_causes = doc.extracted_causes or ext_causes
                ext_snippet = doc.extracted_ai_snippet or ext_snippet
            
            # 감지 레벨 계산용 임시 객체 (원본 보호)
            c_copy = copy.copy(c)
            c_copy.extracted_ai_snippet = ext_snippet
            c_copy.extracted_causes = ext_causes
            score = calculate_case_detection_score(c_copy)
            scored_cases.append((score, c, ext_causes, ext_snippet))
            
        scored_cases.sort(key=lambda x: (x[0], x[1].recent_updates if x[1].recent_updates != "미확인" else ""), reverse=True)

        for idx, (score, c, extracted_causes, extracted_ai_snippet) in enumerate(scored_cases, start=1):             
                slug = _slugify_case_name(c.case_name)
                docket_url = f"https://www.courtlistener.com/docket/{c.docket_id}/{slug}/"
      
                complaint_doc_no = c.complaint_doc_no
                complaint_link = c.complaint_link
                
                if c.docket_id in doc_map:
                    doc = doc_map[c.docket_id]
                    complaint_doc_no = doc.doc_number or doc.doc_type
                    complaint_link = doc.document_url or doc.pdf_url
             
                if c.court_short_name and c.court_api_url:
                    court_display = _mdlink(c.court_short_name, c.court_api_url)
                else:
                    court_display = _esc(c.court)

                # =====================================================
                # FIX: Complaint PDF 링크 표시 규칙
                # - 링크 존재 시: 📄 아이콘 출력
                # - 링크 없으면: "-"
                # =====================================================
                if complaint_link:
                    complaint_link_display = _mdlink("📄", complaint_link)
                else:
                    complaint_link_display = "-"

                # =====================================================
                # NEW: RECAP 테이블 로그 출력
                # =====================================================
                debug_log(f"RECAP row added: case={c.case_name}, docket={c.docket_number}, detection={score}")

                # =====================================================
                # NEW: Nature 필드 강조 처리
                # - 820 Copyright → 빨간색 표시
                # =====================================================
                nature_display = _esc(c.nature_of_suit)
                if (c.nature_of_suit or "").strip() == "820 Copyright":
                    nature_display = '⚠️**820 Copyright**'

                # 데이터 성격에 따른 아이콘 결정
                icon = _get_data_icon(f"{c.case_name} {c.nature_of_suit} {c.cause} {extracted_causes} {extracted_ai_snippet}")
                
                lines.append(
                    f"| {idx} | "
                    f"{_esc(c.status)} | "
                    f"{icon} {_mdlink(c.case_name, docket_url)} | "
                    f"{_mdlink(c.docket_number, docket_url)} | "
                    f"{nature_display} | "
                    f"{format_detection_level(score)} | "
                    f"{_short(extracted_causes, 120)} | "
                    f"{_short(extracted_ai_snippet, 120)} | "
                    f"{_esc(c.cause)} | "
                    f"{_esc(c.judge)} | "
                    f"{court_display} | "
                    f"{_esc(complaint_doc_no)} | "
                    f"{complaint_link_display} | "
                    f"{_esc(c.recent_updates)} |"
                )
        lines.append("")
    else:
        lines.append("새로운 소식이 0건입니다.\n")

    # =====================================================
    # NEW: Samsung Cases
    # =====================================================
    samsung_cases = []
    if cl_cases:
        for score, c, ext_causes, ext_snippet in scored_cases:
            case_name_lower = (c.case_name or "").lower()
            text_lower = f"{ext_causes or ''} {ext_snippet or ''} {c.cause or ''}".lower()
            
            # 피고가 Samsung인지 대략적으로 파악하기 위해 v. 뒷부분 검사
            import re
            parts = re.split(r'\s+v\.?\s+|\s+vs\.?\s+', case_name_lower)
            # 만약 다중 소송 병합 등으로 v. 가 여러번 들어갔을 경우를 대비해 첫 v. 이후의 모든 텍스트를 피고측으로 간주
            defendant_part = " ".join(parts[1:]) if len(parts) > 1 else case_name_lower
            
            # 대소문자 구분 없이(이미 lower 적용됨) 피고측 문자열에 samsung이 포함되어 있는지 확인
            if "samsung" in defendant_part and "train" in text_lower:
                samsung_cases.append((score, c, ext_causes, ext_snippet))

    lines.append("### ⚖️ Samsung Cases (Courtlistener+RECAP)")
    lines.append(
        f"감지된 소송 사건이 {len(samsung_cases)}건입니다. "
        f"<details><summary><strong>🔍 Samsung 소송 사건 검색 기준 </strong></summary>"
        f"피고가 \"Samsung\" 이면서, 소장문서에 \"train\" 단어가 포함되어 있는 소송건들입니다.</details>"
    )
    
    if samsung_cases:
        lines.append(
            "| No. | 상태 | 케이스명 | 도켓번호 | Nature | 감지 레벨⬇️ | "
            "소송이유 | AI학습관련 핵심주장 | 법적 근거 | 담당판사 | 법원 | "
            "Complaint 문서 번호 | Complaint PDF 링크 | 최근 도켓 업데이트 |"
        )
        lines.append(_md_sep(14))

        for idx, (score, c, extracted_causes, extracted_ai_snippet) in enumerate(samsung_cases, start=1):             
            slug = _slugify_case_name(c.case_name)
            docket_url = f"https://www.courtlistener.com/docket/{c.docket_id}/{slug}/"
  
            complaint_doc_no = c.complaint_doc_no
            complaint_link = c.complaint_link
            
            if cl_cases and c.docket_id in doc_map:
                doc = doc_map[c.docket_id]
                complaint_doc_no = doc.doc_number or doc.doc_type
                complaint_link = doc.document_url or doc.pdf_url
         
            if c.court_short_name and c.court_api_url:
                court_display = _mdlink(c.court_short_name, c.court_api_url)
            else:
                court_display = _esc(c.court)

            if complaint_link:
                complaint_link_display = _mdlink("📄", complaint_link)
            else:
                complaint_link_display = "-"

            nature_display = _esc(c.nature_of_suit)
            if (c.nature_of_suit or "").strip() == "820 Copyright":
                nature_display = '⚠️**820 Copyright**'

            icon = _get_data_icon(f"{c.case_name} {c.nature_of_suit} {c.cause} {extracted_causes} {extracted_ai_snippet}")
            
            lines.append(
                f"| {idx} | "
                f"{_esc(c.status)} | "
                f"{icon} {_mdlink(c.case_name, docket_url)} | "
                f"{_mdlink(c.docket_number, docket_url)} | "
                f"{nature_display} | "
                f"{format_detection_level(score)} | "
                f"{_short(extracted_causes, 120)} | "
                f"{_short(extracted_ai_snippet, 120)} | "
                f"{_esc(c.cause)} | "
                f"{_esc(c.judge)} | "
                f"{court_display} | "
                f"{_esc(complaint_doc_no)} | "
                f"{complaint_link_display} | "
                f"{_esc(c.recent_updates)} |"
            )
        lines.append("")


    # RECAP 법원 문서 (.pdf format)
    if cl_docs:
        lines.append("<details>")        
        lines.append("<summary><strong><span style=\"font-size:2.5em; font-weight:bold;\">📄 Cases: 법원 문서 기반 (Complaint/Petition 우선)</span></strong></summary>")
        lines.append("")
        lines.append("| No. | 제출일⬇️ | 케이스 | 문서유형 | 법원 문서 |")
        lines.append(_md_sep(5))

        # 제출일 기준 내림차순 정렬
        sorted_docs = sorted(
            cl_docs,
            key=lambda x: x.date_filed or "",
            reverse=True
        )

        for idx, d in enumerate(sorted_docs, start=1):
            link = d.document_url or d.pdf_url
            lines.append(
                f"| {idx} | "
                f"{_esc(d.date_filed)} | {_esc(d.case_name)} | "
                f"{_esc(d.doc_type)} | {_mdlink('📄', link)} |"
            )
        lines.append("</details>\n")

    # 기사 주소
    if lawsuits:
        lines.append("<details>")
        lines.append("<summary><strong><span style=\"font-size:2.5em; font-weight:bold;\">📰 News Website</span></strong></summary>")
        lines.append("")
        for s in lawsuits:
            lines.append(f"### {_esc(s.article_title or s.case_title)}")
            for u in s.article_urls:
                lines.append(f"- {u}")
        lines.append("</details>\n")

    # 감지 레벨 척도
    lines.append("<details>")
    lines.append("<summary><strong><span style=\"font-size:2.5em; font-weight:bold;\">📘 비인가 데이터 학습 소송 감지 레벨(0~100) 평가 척도</span></strong></summary>")
    lines.append("")
    lines.append("- 해당 건이 비인가 데이터 학습 소송과 얼마나 밀접한지를 표현하며 리스크 강도를 수치화한 지표입니다.")
    lines.append("- 0에 가까울수록 → 간접/주변 이슈")
    lines.append("- 100에 가까울수록 → 비인가 학습 핵심 감지 사건\n")
    lines.append("")
    
    lines.append("### 📊 등급 기준 (Detection Level)")
    lines.append("- -10 ~ 0 🤝 : Data 정식 계약/협력 (Low)")
    lines.append("-  0~ 39 🟢 : 간접 연관 (Low)")
    lines.append("- 40~ 59 🟡 : 학습 쟁점 존재 (Medium)")
    lines.append("- 60~ 79 ⚠️ : 모델 학습 직접 언급 (High)")
    lines.append("- 80~100 🔥 : 무단 수집 + 학습 + 상업적 사용 (Critical High)")
    lines.append("- (참고) 정식 계약/협력 발생 시 감지 레벨 점수를 -10점 차감하여 실제 비인가 학습 소송 이슈와 차별화하였습니다. (최소 0점 보정 포함)\n")
    lines.append("")

    lines.append("### 🧮 점수 산정 기준 (비인가 데이터 학습 소송 감지 기준)")
    lines.append("")
    lines.append("| 항목 | 조건 (주요 키워드) | 점수 |")
    lines.append("|---|---|---|")
    lines.append("| **핵심 AI 학습 저작권 소송** | **(820/Copyright) + (Train/Training)** | **+50** |")
    for name, keywords, points in DETECTION_CRITERIA:
        kw_str = ", ".join(keywords[:5]) + " 등"
        sign = "+" if points > 0 else ""
        lines.append(f"| {name} | {kw_str} | {sign}{points} |")
    lines.append("\n- **핵심 가점 항목**: 저작권 소송(Nature 820 등)이면서 소장 내에 모델 학습(Train/Training) 키워드가 동시에 발견될 경우 **+50점**의 추가 가점을 부여하여 최상단에 우선 노출합니다.")
    lines.append("- **감지 레벨 산정 로직 개선**: 정식 계약/협력 발생 시 감지 레벨 점수를 -10점 차감하여 실제 비인가 학습 소송 이슈와 차별화하였습니다. (최소 0점 보정 포함)")
    lines.append("")

    lines.append("</details>\n")

    return "\n".join(lines)


def _get_data_category(text: str) -> str:
    """대상 데이터의 카테고리를 텍스트 기반으로 추정합니다."""
    h = (text or "").lower()
    if any(k in h for k in ["book", "novel", "author", "writing", "literary", "library", "shadow library", "pirat", "books3", "prose"]): return "Authors/Books"
    if any(k in h for k in ["music", "lyrics", "audio", "song", "musical", "singer", "artist", "record", "spotify", "warner", "sony", "universal"]): return "Music/Recordings"
    if any(k in h for k in ["video", "youtube", "movie", "film", "netflix", "vimeo", "motion picture"]): return "Video/Film"
    if any(k in h for k in ["image", "photo", "picture", "art", "style", "drawing", "illustration", "artwork", "photographer", "getty", "deviantart", "midjourney", "stable diffusion", "stock"]): return "Visual Art"
    if any(k in h for k in ["news", "article", "journalism", "times", "newspaper", "press", "reporting"]): return "News"
    if any(k in h for k in ["publisher", "proquest", "elsevier", "springer", "wiley", "academic", "journal", "media"]): return "Publishers"
    if any(k in h for k in ["voice", "likeness", "personality", "biometric", "avatar", "deepfake", "speech", "vocal", "name and likeness"]): return "Voice/Likeness"
    if any(k in h for k in ["code", "software", "programming", "github", "source code", "developer", "copilot", "git"]): return "Code/Software"
    return "Other"


