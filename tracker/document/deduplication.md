# 🔁 유사도 측정 & 중복 제거(Deduplication) 가이드

> **대상**: 텍스트 유사도 측정 방법론과 이 프로젝트에서 적용한 다단계 중복 제거 파이프라인을 학습합니다.  
> **관련 파일**: [`src/dedup.py`](../src/dedup.py), [`src/gemini.py`](../src/gemini.py)

---

## 1. 왜 중복 제거가 필요한가?

이 프로젝트는 **시간당 1회** 자동 실행되어 뉴스·소송 데이터를 수집합니다. 같은 기사나 소송 사건이 여러 번 실행에서 반복 감지되는 문제가 발생합니다.

| 문제 상황 | 예시 |
|----------|------|
| 동일 기사 중복 | "OpenAI 저작권 소송" 기사가 매 시간마다 등장 |
| 제목만 다른 동의어 기사 | "OpenAI sued for copyright" ≈ "Authors sue OpenAI over training data" |
| 동일 도켓 번호의 소송 | `1:23-cv-11195` 소송이 매일 재등록 |

---

## 2. 이 프로젝트의 중복 제거 전략 개요

```
새 데이터 입력
    │
    ▼
[1단계] 정확한 문자열 일치 (Exact Match)
    │  제목/도켓번호 완전 일치 → 즉시 제거
    ▼
[2단계] BM25 키워드 유사도 (옵션: BM25_SEMANTIC_DEDUP=1)
    │  핵심 단어 기반 유사도 점수 → 임계값 초과 시 제거
    ▼
[3단계] 의미론적 임베딩 유사도 (옵션: GEMINI_SEMANTIC_DEDUP=1)
    │  Gemini 벡터 임베딩 + 코사인 유사도 → 임계값 초과 시 제거
    ▼
[4단계] 배치 내부 중복 제거 (Intra-batch Dedup)
    │  현재 실행 배치 내의 중복도 제거
    ▼
결과: 중복 제거 요약 + 신규 항목만 출력
```

---

## 3. 1단계: 정확한 문자열 일치 (Exact Match)

가장 단순하고 빠른 방법입니다. 이전 GitHub 댓글들에서 **기사 제목**과 **도켓 번호**를 Set으로 수집하여 O(1) 조회합니다.

### 구현 ([`src/dedup.py`](../src/dedup.py))

```python
# 이전 댓글에서 기준(Baseline) Set 구성
base_article_set: Set[str] = set()
base_docket_set:  Set[str] = set()

for comment in previous_comments:
    body = comment.get("body") or ""

    # 뉴스 제목 추출 → Set에 추가
    news_section = extract_section(body, "### 📰 AI Suit News")
    headers, rows, _ = parse_table(news_section)
    if "제목" in headers:
        for row in rows:
            title = extract_article_title(row[headers.index("제목")])
            if title:
                base_article_set.add(title)

    # 도켓 번호 추출 → Set에 추가
    case_section = extract_section(body, "### ⚖️ Cases")
    headers, rows, _ = parse_table(case_section)
    if "도켓번호" in headers:
        for row in rows:
            docket = extract_article_title(row[headers.index("도켓번호")])
            if docket:
                base_docket_set.add(docket)

# 현재 기사 중 기준 Set에 있으면 제거
for title in current_titles:
    if title in base_article_set:
        print(f"[중복] 정확 일치 제거: {title}")
    else:
        new_items.append(title)
```

### 특징

| 항목 | 내용 |
|------|------|
| 속도 | ⚡ O(1) — 매우 빠름 |
| 정확도 | 완전 동일한 텍스트만 제거 |
| 한계 | 표현이 조금만 달라도 미탐지 |
| 비용 | 무료 (API 없음) |

---

## 4. 2단계: BM25 키워드 유사도

**BM25(Best Match 25)**는 검색 엔진에서 널리 사용되는 단어 빈도 기반 유사도 알고리즘입니다. TF-IDF의 개선 버전으로, 단어 빈도와 문서 길이를 고려합니다.

### BM25 점수 공식

$$\text{score}(D, Q) = \sum_{i=1}^{n} \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$

- `f(q_i, D)`: 문서 D에서 단어 q_i의 빈도
- `|D|`: 문서 길이, `avgdl`: 평균 문서 길이
- `k_1 = 1.5`, `b = 0.75` (기본 파라미터)

### 구현

```python
from rank_bm25 import BM25Okapi

# 기준 제목들을 토크나이즈
tokenized_corpus = [title.lower().split() for title in base_titles]
bm25 = BM25Okapi(tokenized_corpus)

# 현재 기사 제목으로 유사도 점수 계산
query = "OpenAI sued for copyright infringement training data".lower().split()
scores = bm25.get_scores(query)  # 각 기준 제목에 대한 점수 배열

# 임계값 초과 시 중복으로 판단
threshold = 3.0   # 환경변수 BM25_DEDUP_THRESHOLD로 조정 가능
if max(scores) >= threshold:
    print(f"[BM25 중복] 유사도 점수: {max(scores):.4f}")
```

### 활성화 방법

```bash
# GitHub Actions Variables에 추가
BM25_SEMANTIC_DEDUP=1        # BM25 활성화 (기본: 비활성)
BM25_DEDUP_THRESHOLD=3.0     # 임계값 (높을수록 엄격)
```

### 특징

| 항목 | 내용 |
|------|------|
| 속도 | 🚀 빠름 (로컬 계산) |
| 정확도 | 유사 표현, 같은 키워드 기사 탐지 |
| 한계 | 동의어, 다른 언어 표현은 미탐지 |
| 비용 | 무료 (`rank_bm25` 라이브러리) |
| 라이브러리 | `pip install rank_bm25` |

### BM25 점수 해석

| 점수 범위 | 의미 |
|----------|------|
| 0 ~ 1.0 | 거의 다른 내용 |
| 1.0 ~ 3.0 | 일부 키워드 공유 |
| 3.0 ~ 6.0 | 매우 유사한 내용 ← 기본 임계값 |
| 6.0+ | 사실상 동일 내용 |

---

## 5. 3단계: 의미론적 임베딩 유사도 (Semantic Similarity)

텍스트를 **고차원 벡터(임베딩)**로 변환한 후 **코사인 유사도**를 계산하는 방법입니다. 표현이 달라도 의미가 같으면 탐지 가능합니다.

### 임베딩(Embedding)이란?

텍스트를 수백~수천 차원의 숫자 벡터로 변환하는 기술입니다.

```
"OpenAI 저작권 소송" → [0.12, -0.34, 0.89, ..., 0.45]  (3072차원)
"Authors sue OpenAI" → [0.11, -0.35, 0.88, ..., 0.44]  (3072차원)
                                                    ↑
                                           거의 같은 방향 → 유사도 ≈ 0.97
```

### Gemini 임베딩 API 사용

```python
from google import genai
from google.genai import types

client = genai.Client(api_key="YOUR_GEMINI_API_KEY")

# 단일 텍스트 임베딩
response = client.models.embed_content(
    model="models/gemini-embedding-2",   # 최신 고성능 모델
    contents=["OpenAI 저작권 소송"],
    config=types.EmbedContentConfig(
        task_type="RETRIEVAL_DOCUMENT"    # 검색/유사도 목적
    )
)
embedding = response.embeddings[0].values
print(f"임베딩 차원: {len(embedding)}")  # 3072

# 여러 텍스트 일괄 처리
response = client.models.embed_content(
    model="models/gemini-embedding-2",
    contents=[
        "OpenAI 저작권 소송",
        "Authors sue OpenAI over training data",
        "삼성전자 갤럭시 AI",
    ],
    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
)
embeddings = [emb.values for emb in response.embeddings]
```

### 이 프로젝트의 임베딩 구현 ([`src/gemini.py`](../src/gemini.py))

```python
def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Gemini API를 사용하여 텍스트 리스트의 임베딩을 생성합니다."""
    client = genai.Client(api_key=api_key)

    try:
        # 1순위: 최신 고성능 모델
        response = client.models.embed_content(
            model="models/gemini-embedding-2",
            contents=texts,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
        )
        return [emb.values for emb in response.embeddings]

    except Exception:
        # 2순위: 안정적인 fallback 모델
        response = client.models.embed_content(
            model="models/gemini-embedding-001",
            contents=texts,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
        )
        return [emb.values for emb in response.embeddings]
```

---

## 6. 코사인 유사도 (Cosine Similarity)

두 벡터 간의 **방향 일치도**를 -1 ~ 1 사이의 값으로 표현합니다.

### 공식

$$\text{cosine\_similarity}(A, B) = \frac{A \cdot B}{\|A\| \cdot \|B\|} = \frac{\sum_{i} A_i B_i}{\sqrt{\sum_{i} A_i^2} \cdot \sqrt{\sum_{i} B_i^2}}$$

### 이 프로젝트의 구현 ([`src/gemini.py`](../src/gemini.py))

```python
def calculate_cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """두 임베딩 벡터 간의 코사인 유사도를 계산합니다."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = sum(a * a for a in v1) ** 0.5
    norm_v2 = sum(a * a for a in v2) ** 0.5

    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0

    return dot_product / (norm_v1 * norm_v2)
```

### 유사도 값 해석

| 코사인 유사도 | 의미 | 예시 |
|-------------|------|------|
| **0.95 ~ 1.0** | 사실상 동일 | 같은 기사 다른 출처 |
| **0.85 ~ 0.95** | 매우 유사 ← 기본 임계값 | 같은 사건 다른 표현 |
| **0.70 ~ 0.85** | 관련 있음 | 같은 주제 다른 관점 |
| **0.50 ~ 0.70** | 약간 관련 | 동일 분야 다른 내용 |
| **0.0 ~ 0.50** | 무관 | 전혀 다른 내용 |

### 활성화 방법

```bash
# GitHub Actions Variables에 추가
GEMINI_SEMANTIC_DEDUP=1        # 시맨틱 중복 제거 활성화
SEMANTIC_DEDUP_THRESHOLD=0.85  # 임계값 (낮출수록 더 많이 제거)
```

### 특징

| 항목 | 내용 |
|------|------|
| 속도 | 🐢 느림 (API 호출 필요) |
| 정확도 | 🎯 가장 높음 — 의미 기반 탐지 |
| 한계 | API 비용·속도 제한 |
| 비용 | Gemini API 토큰 소비 |
| 모델 | `gemini-embedding-2` (3072차원) |

---

## 7. 4단계: 배치 내부 중복 제거 (Intra-batch Dedup)

같은 실행 배치 내에서도 수집된 기사들 간의 중복을 제거합니다. 예를 들어 4개의 뉴스 쿼리에서 같은 기사가 2번 수집되는 경우를 처리합니다.

```python
accepted_indices = []      # 통과된 기사 인덱스
dup_details = {}           # 중복 유형별 횟수 추적

for i in surviving_indices:
    is_dup = False

    for acc_idx in accepted_indices:
        # 1. 정확한 제목 일치
        if title_i.lower() == title_acc.lower():
            is_dup = True; dup_type = "제목"; break

        # 2. BM25 유사도 (옵션)
        if enable_bm25 and bm25_score >= threshold:
            is_dup = True; dup_type = "키워드"; break

        # 3. 의미론적 유사도 (옵션)
        if enable_semantic and cosine_sim >= threshold:
            is_dup = True; dup_type = "의미"; break

    if is_dup:
        dup_details[acc_idx][dup_type] += 1   # 원본에 중복 횟수 기록
    else:
        accepted_indices.append(i)             # 신규로 통과
```

### 중복 건수 출력 형식

GitHub Issue 테이블에서 `중복건수` 컬럼에 표시됩니다:
```
0                    → 중복 없음
2 (제목:1, 키워드:1)  → 2건 중복, 제목일치 1건 + BM25 1건
3 (의미:3)           → 의미론적으로 유사한 기사 3건
```

---

## 8. 전체 중복 제거 흐름 (dedup.py)

```python
# src/run.py에서 호출
md, new_news_count, new_cases_count = apply_deduplication(md, all_baseline_comments)

# 내부 처리 순서:
# 1. 이전 댓글에서 baseline 세트 구성
# 2. 정확 일치 → BM25 → 시맨틱 순으로 필터링
# 3. 배치 내부 중복 제거
# 4. 중복 제거 요약 헤더 생성
```

### 중복 제거 요약 출력 예시

```
### 중복 제거 요약:
🔁 Dedup Summary
└ News 42 (Baseline): 10 (Dup), **5 (New)** 🔴
└ Cases 18 (Baseline): 2 (Dup), **3 (New)** 🔴
└ Docs: **2 (New)** 🔴
```

---

## 9. 환경변수 설정 요약

| 환경변수 | 기본값 | 설명 |
|---------|--------|------|
| `BM25_SEMANTIC_DEDUP` | `0` | BM25 중복 제거 활성화 (`1`=ON) |
| `BM25_DEDUP_THRESHOLD` | `3.0` | BM25 점수 임계값 |
| `GEMINI_SEMANTIC_DEDUP` | `0` | 시맨틱 임베딩 중복 제거 활성화 (`1`=ON) |
| `SEMANTIC_DEDUP_THRESHOLD` | `0.85` | 코사인 유사도 임계값 (0~1) |
| `PREVIOUS_ITEM_DEDUP_DAYS` | 없음 | 이전 N개 이슈를 baseline으로 포함 |

### 설정 예시 (GitHub Actions Variables)
```
# 최소 설정 (기본: 정확 일치만)
PREVIOUS_ITEM_DEDUP_DAYS=3

# 중간 설정 (BM25 추가)
BM25_SEMANTIC_DEDUP=1
BM25_DEDUP_THRESHOLD=3.5

# 최강 설정 (BM25 + 시맨틱)
BM25_SEMANTIC_DEDUP=1
GEMINI_SEMANTIC_DEDUP=1
SEMANTIC_DEDUP_THRESHOLD=0.87
```

---

## 10. 각 알고리즘 비교 요약

| 알고리즘 | 속도 | 정확도 | 비용 | 활성화 |
|---------|------|--------|------|--------|
| **정확 일치** | ⚡ 매우 빠름 | ★★☆ | 무료 | 항상 ON |
| **BM25** | 🚀 빠름 | ★★★ | 무료 | 옵션 |
| **시맨틱 임베딩** | 🐢 느림 | ★★★★★ | API 비용 | 옵션 |

---

## 11. 실전 테스트 예시

```python
# scratch/test_similarity.py

# 1. 코사인 유사도 테스트
from src.gemini import get_embeddings, calculate_cosine_similarity

texts = [
    "OpenAI sued for copyright infringement over training data",
    "Authors file lawsuit against OpenAI for unauthorized use of books",
    "Samsung Galaxy AI features announcement",
]

embeddings = get_embeddings(texts)

# 기사 0 vs 기사 1 (유사한 내용)
sim_01 = calculate_cosine_similarity(embeddings[0], embeddings[1])
print(f"유사도 (OpenAI소송 vs Authors소송): {sim_01:.4f}")  # ~0.90+

# 기사 0 vs 기사 2 (다른 내용)
sim_02 = calculate_cosine_similarity(embeddings[0], embeddings[2])
print(f"유사도 (OpenAI소송 vs Samsung): {sim_02:.4f}")       # ~0.40~

# 2. BM25 테스트
from rank_bm25 import BM25Okapi

corpus = ["openai sued copyright infringement training data".split()]
bm25 = BM25Okapi(corpus)

query1 = "authors file lawsuit openai unauthorized books".split()
query2 = "samsung galaxy ai features".split()

print(f"BM25 (유사 기사): {max(bm25.get_scores(query1)):.4f}")  # 높음
print(f"BM25 (무관 기사): {max(bm25.get_scores(query2)):.4f}")  # 낮음
```

---

## 12. 참고 자료

| 링크 | 설명 |
|------|------|
| [BM25 논문 (Wikipedia)](https://en.wikipedia.org/wiki/Okapi_BM25) | BM25 알고리즘 원리 |
| [rank_bm25 라이브러리](https://pypi.org/project/rank-bm25/) | Python BM25 구현체 |
| [Gemini Embeddings API](https://ai.google.dev/api/embeddings) | 임베딩 생성 공식 문서 |
| [코사인 유사도 (Wikipedia)](https://en.wikipedia.org/wiki/Cosine_similarity) | 유사도 공식 |
| [SBERT (Sentence-BERT)](https://sbert.net/) | 로컬 임베딩 모델 (Gemini 대안) |
