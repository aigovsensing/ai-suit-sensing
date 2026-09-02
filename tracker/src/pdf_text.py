from __future__ import annotations
from io import BytesIO
from typing import Optional
import requests
from pypdf import PdfReader


_EVIDENCE_TERMS = (
    "dataset", "data set", "training data", "train", "trained", "training",
    "copied", "copying", "scraped", "scraping", "downloaded", "pirated",
    "books3", "libgen", "library genesis", "z-library", "bibliotik",
    "anna's archive", "anna’s archive", "laion", "common crawl",
)


def _relevant_excerpt(text: str, radius: int = 700) -> str:
    """데이터셋/학습 증거 주변 문맥을 페이지에서 압축해 반환한다."""
    lower = text.lower()
    positions = [lower.find(term) for term in _EVIDENCE_TERMS]
    positions = [pos for pos in positions if pos >= 0]
    if not positions:
        return ""
    start = max(0, min(positions) - radius)
    end = min(len(text), max(positions) + radius)
    return text[start:end]

def extract_pdf_text(url: str, max_chars: int = 6000, timeout: int = 30) -> str:
    """소장 PDF의 앞부분과 문서 전체의 데이터셋 관련 문맥을 추출한다.

    종전에는 앞 10페이지만 읽고 글자 수가 차면 중단했기 때문에, 사실관계가 뒤쪽에
    기재된 긴 소장에서 데이터셋 이름을 놓쳤다. 이제 최대 100페이지를 훑되 앞부분과
    관련 키워드 주변만 보존해 반환 크기는 ``max_chars`` 이내로 제한한다.
    스캔 이미지 PDF는 별도 OCR이 없으므로 빈 문자열이 될 수 있다.
    """
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        bio = BytesIO(r.content)
        reader = PdfReader(bio)
        front_chunks = []
        evidence_chunks = []
        front_budget = max(800, max_chars // 3)
        for i, page in enumerate(reader.pages[:100]):
            try:
                t = page.extract_text() or ""
            except Exception:
                t = ""
            if t:
                if sum(len(c) for c in front_chunks) < front_budget:
                    front_chunks.append(t)
                excerpt = _relevant_excerpt(t)
                if excerpt:
                    evidence_chunks.append(excerpt)
        front = " ".join("\n".join(front_chunks).split())[:front_budget]
        # 같은 앞쪽 문맥이 evidence에도 잡힐 수 있으므로 순서를 유지하며 중복 제거한다.
        evidence = " ".join("\n".join(dict.fromkeys(evidence_chunks)).split())
        remaining = max(0, max_chars - len(front) - 1)
        return (front + " " + evidence[:remaining]).strip()
    except Exception:
        return ""
