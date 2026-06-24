from __future__ import annotations
from io import BytesIO
from typing import Optional
import requests
from pypdf import PdfReader

def extract_pdf_text(url: str, max_chars: int = 6000, timeout: int = 30) -> str:
    """PDF 텍스트 추출(가벼운 형태).
    - 스캔 PDF(이미지)면 텍스트가 거의 없을 수 있음.
    """
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        bio = BytesIO(r.content)
        reader = PdfReader(bio)
        chunks = []
        for i, page in enumerate(reader.pages[:10]):  # 앞쪽만
            try:
                t = page.extract_text() or ""
            except Exception:
                t = ""
            if t:
                chunks.append(t)
            if sum(len(c) for c in chunks) >= max_chars:
                break
        text = "\n".join(chunks)
        text = " ".join(text.split())
        return text[:max_chars]
    except Exception:
        return ""
