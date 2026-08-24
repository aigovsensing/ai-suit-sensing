from __future__ import annotations
import re
from typing import List, Tuple

KNOWN_DATASETS = (
    ("Objaverse-XL", re.compile(r"\bobjaverse[\s-]*xl\b", re.I)),
    ("Books3", re.compile(r"\bbooks\s*3\b", re.I)),
    ("The Pile", re.compile(r"\bthe\s+pile\b", re.I)),
    ("LAION-5B", re.compile(r"\blaion[\s-]*5b\b", re.I)),
    ("LAION-400M", re.compile(r"\blaion[\s-]*400m\b", re.I)),
    ("Common Crawl", re.compile(r"\bcommon\s+crawl\b", re.I)),
    ("C4", re.compile(r"\b(?:the\s+)?c4\s+dataset\b", re.I)),
    ("RedPajama", re.compile(r"\bred\s*pajama\b", re.I)),
)

DATASET_URLS = {
    "Objaverse-XL": "https://github.com/allenai/objaverse-xl",
    "The Pile": "https://pile.eleuther.ai/",
    "LAION-5B": "https://laion.ai/blog/laion-5b/",
    "LAION-400M": "https://laion.ai/blog/laion-400-open-dataset/",
    "Common Crawl": "https://commoncrawl.org/",
    "RedPajama": "https://github.com/togethercomputer/RedPajama-Data",
}

CAUSE_PATTERNS = [
    ("저작권 침해", re.compile(r"\bcopyright\s+infringement\b", re.I)),
    ("DMCA(우회/기술적 보호조치)", re.compile(r"\bdmca\b|digital\s+millennium\s+copyright\s+act|circumvent", re.I)),
    ("계약 위반/약관 위반", re.compile(r"breach\s+of\s+contract|terms\s+of\s+service|terms\s+of\s+use", re.I)),
    ("부정경쟁/불공정행위", re.compile(r"unfair\s+competition|unlawful\s+business\s+practice|u\.?c\.?l\.?|cal\.?\s+bus\.?\s+&\s+prof\.?\s*code\s*§?\s*17200", re.I)),
    ("컴퓨터침입(CFAA)", re.compile(r"\bcfaa\b|computer\s+fraud\s+and\s+abuse\s+act", re.I)),
    ("전환/부당이득", re.compile(r"conversion|unjust\s+enrichment|restitution", re.I)),
    ("상표/랜햄법", re.compile(r"lanham\s+act|trademark", re.I)),
    ("영업비밀", re.compile(r"trade\s+secret|dtSA|defend\s+trade\s+secrets\s+act", re.I)),
]

AI_DATA_PATTERNS = [
    re.compile(r"train(?:ing|ed)?\s+(?:an\s+)?(?:ai|model|models|llm|large\s+language\s+model|gpt|transformer|diffusion)", re.I),
    re.compile(r"training\s+data|dataset|scrap(?:e|ing)|web\s+scrap|harvest(?:ing)?|mining|extraction|collection", re.I),
    re.compile(r"without\s+permission|unauthorized|without\s+license|pirat(?:ed|ing)|shadow\s+library|bypass|robots\.txt", re.I),
    re.compile(r"commercial|profit|monetiz(?:e|ation)|revenue|subscription|enterprise", re.I),
]

def _sentences(text: str) -> List[str]:
    # 너무 거친 문장 분리지만, 스니펫에서는 충분
    parts = re.split(r"(?<=[\.\?!])\s+", text)
    return [p.strip() for p in parts if p and len(p.strip()) > 10]

def detect_causes(text: str) -> List[str]:
    found = []
    for name, pat in CAUSE_PATTERNS:
        if pat.search(text):
            found.append(name)
    return found

def extract_ai_training_snippet(text: str, max_len: int = 280) -> str:
    sents = _sentences(text)
    scored: List[Tuple[int, str]] = []
    for s in sents:
        score = 0
        for pat in AI_DATA_PATTERNS:
            if pat.search(s):
                score += 1
        if score:
            scored.append((score, s))
    if not scored:
        # fallback: 키워드만이라도 있는 구간 (re.DOTALL 추가하여 줄바꿈 대응)
        m = re.search(r".{0,80}(training\s+data|dataset|scrap(?:e|ing)|pirat(?:ed|ing)|unauthorized).{0,180}", text, re.I | re.DOTALL)
        if m:
            sn = re.sub(r"\s+", " ", m.group(0)).strip()
            return (sn[:max_len] + "…") if len(sn) > max_len else sn
        return ""
    scored.sort(key=lambda x: x[0], reverse=True)
    sn = re.sub(r"\s+", " ", scored[0][1]).strip()
    return (sn[:max_len] + "…") if len(sn) > max_len else sn


def extract_dataset_names(text: str) -> List[str]:
    """소장 텍스트에서 명시적으로 이름이 언급된 데이터셋만 반환한다."""
    found = []
    for canonical_name, pattern in KNOWN_DATASETS:
        if pattern.search(text or ""):
            found.append(canonical_name)

    # 알려지지 않은 ``Name Dataset`` 표기도 보존한다. 일반명인 "the dataset"이나
    # "training dataset"은 특정 데이터셋을 가리키지 않으므로 제외한다.
    generic = re.compile(r"\b([A-Z][A-Za-z0-9_.-]*(?:\s+[A-Z][A-Za-z0-9_.-]*){0,3})\s+Dataset\b")
    ignored = {"the", "a", "training", "source", "image", "text"}
    for match in generic.finditer(text or ""):
        name = match.group(1).strip()
        if name.lower() not in ignored and name not in found:
            found.append(name)
    return found


def dataset_url(name: str) -> str:
    """검증된 공식 프로젝트 주소가 있는 데이터셋에 대해서만 URL을 제공한다."""
    return DATASET_URLS.get(name, "")


def extract_dataset_allegation(text: str, names: List[str], max_len: int = 220) -> str:
    """데이터셋 이름이 실제로 들어간 소장 문장을 우선하여 관련 주장을 반환한다."""
    normalized = re.sub(r"<[^>]+>", " ", text or "")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    candidates = _sentences(normalized)
    for sentence in candidates:
        if any(re.search(re.escape(name), sentence, re.I) for name in names):
            return (sentence[:max_len] + "…") if len(sentence) > max_len else sentence
    return extract_ai_training_snippet(normalized, max_len=max_len)

def extract_parties_from_caption(text: str) -> tuple[str, str]:
    # 흔한 캡션 패턴: "PLAINTIFF, v. DEFENDANT,"
    # 캡션은 보통 문서 상단에 있으므로 앞부분만 검사
    cap = text[:2500]
    
    # 1. 정교한 패턴: "PLAINTIFF_NAME, [et al.,] Plaintiff(s), v. DEFENDANT_NAME, [et al.,] Defendant(s)"
    # [A-Z0-9]로 시작하고 특수문자 포함 가능하도록 개선
    m = re.search(r"([A-Z0-9][A-Z0-9 ,.&'\-]{2,}?)\s*,\s*(?:et\s+al\.)?\s*Plaintiff[s]?\s*,?\s*v\.?\s*([A-Z0-9][A-Z0-9 ,.&'\-]{2,}?)\s*,\s*(?:Defendant[s]?|\b)", cap, re.I)
    if m:
        p = re.sub(r"\s+", " ", m.group(1)).strip(" ,")
        d = re.sub(r"\s+", " ", m.group(2)).strip(" ,")
        # 법원 이름 등이 잡히는 것 방지 (보통 DISTRICT COURT 등)
        if "DISTRICT" not in p.upper() and "COURT" not in p.upper():
            return p, d

    # 2. 더 단순: "X v. Y" (대소문자 구분 없이 검색하되, 결과는 정리)
    m2 = re.search(r"([A-Z0-9][A-Za-z0-9 ,.&'\-]{2,})\s+v\.?\s+([A-Z0-9][A-Za-z0-9 ,.&'\-]{2,})", cap, re.I)
    if m2:
        p2 = m2.group(1).strip()
        d2 = m2.group(2).strip()
        if "DISTRICT" not in p2.upper() and "COURT" not in p2.upper():
            return p2, d2
            
    return "미확인", "미확인"
