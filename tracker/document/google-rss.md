# 📰 Google News RSS 피드 사용 가이드

> **대상**: 이 프로젝트에서 뉴스 수집에 Google News RSS를 활용하는 방법을 학습합니다.  
> **관련 파일**: [`src/fetch.py`](../src/fetch.py), [`src/queries.py`](../src/queries.py)

---

## 1. Google News RSS란?

Google News는 RSS(Really Simple Syndication) 피드를 제공하여 특정 키워드, 주제, 지역에 대한 최신 뉴스를 구조화된 XML 형식으로 자동 수집할 수 있게 합니다.

- **프로토콜**: RSS 2.0
- **갱신 주기**: 실시간 (Google 크롤링 주기에 따름)
- **공식 문서**: 없음 (비공식 API), 단 URL 패턴이 안정적으로 유지됨

---

## 2. URL 구조

### 기본 피드 (Top Stories)
```
https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en
```

### 검색어 기반 피드
```
https://news.google.com/rss/search?q=YOUR+QUERY&hl=en-US&gl=US&ceid=US:en
```

### 주제별 피드
```
https://news.google.com/rss/headlines/section/topic/TECHNOLOGY
```

### 지역별 피드
```
https://news.google.com/rss/headlines/section/geo/Seoul
```

---

## 3. URL 파라미터 설명

| 파라미터 | 의미 | 예시 |
|---------|------|------|
| `hl` | Host Language — 인터페이스 언어 | `en-US`, `ko` |
| `gl` | Geolocation — 국가 코드 | `US`, `KR`, `GB` |
| `ceid` | Country-Edition ID — `국가코드:언어코드` | `US:en`, `KR:ko` |
| `q` | 검색 쿼리 (URL 인코딩 필요) | `AI+lawsuit` |

### 주요 언어/지역 조합

| 목적 | `hl` | `gl` | `ceid` |
|------|------|------|--------|
| 미국 영어 뉴스 | `en-US` | `US` | `US:en` |
| 한국 한글 뉴스 | `ko` | `KR` | `KR:ko` |
| 영국 영어 뉴스 | `en-GB` | `GB` | `GB:en` |
| 일본 일어 뉴스 | `ja` | `JP` | `JP:ja` |

---

## 4. 검색 연산자 (q 파라미터)

Google News RSS 검색 쿼리는 **표준 Google 검색 연산자**를 지원합니다.

### 불리언 연산자
```
AI lawsuit copyright          → 모두 포함
"AI training data"            → 정확한 구문 검색
AI OR copyright               → 둘 중 하나 포함
AI -lawsuit                   → lawsuit 제외
```

### 시간 필터
```
AI lawsuit when:1d            → 최근 1일
AI lawsuit when:7d            → 최근 7일
AI lawsuit when:1m            → 최근 1개월
```

### 출처 지정
```
AI lawsuit site:reuters.com   → 특정 사이트 한정
```

### 복합 쿼리 예시 (이 프로젝트에서 사용)
```
("AI training" OR "model training" OR LLM) (lawsuit OR sued OR litigation) (copyright OR pirated OR unauthorized) when:3d
```

---

## 5. Python으로 RSS 파싱하기

이 프로젝트는 `feedparser` 라이브러리를 사용합니다.

### 설치
```bash
pip install feedparser
```

### 기본 사용법
```python
import feedparser

# URL 구성
query = '"AI training" lawsuit copyright when:3d'
encoded_query = query.replace(" ", "%20")
feed_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

# 파싱
feed = feedparser.parse(feed_url)

print(f"피드 제목: {feed.feed.title}")
print(f"수집된 기사 수: {len(feed.entries)}")

for entry in feed.entries:
    print(f"제목: {entry.title}")
    print(f"링크: {entry.link}")
    print(f"발행일: {entry.get('published', 'N/A')}")
    print(f"출처: {entry.source.title if hasattr(entry, 'source') else 'N/A'}")
    print("---")
```

### 이 프로젝트의 실제 구현 ([`src/fetch.py`](../src/fetch.py))
```python
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"

def fetch_news() -> List[NewsItem]:
    items = []
    seen = set()

    for q in NEWS_QUERIES:
        feed_url = GOOGLE_NEWS_RSS.format(q=q.replace(" ", "%20"))
        feed = feedparser.parse(feed_url)

        for e in feed.entries:
            link = getattr(e, "link", "").strip()
            if not link or link in seen:
                continue          # 중복 제거
            seen.add(link)
            items.append(NewsItem(
                title=e.title,
                url=link,
                published_at=parse_dt(e.get("published")),
                source=e.source.title if hasattr(e, "source") else ""
            ))

    # 최신순 정렬
    items.sort(key=lambda x: x.published_at or datetime.min, reverse=True)
    return items
```

---

## 6. RSS 항목(entry) 필드 구조

`feedparser`로 파싱한 각 entry에서 접근 가능한 주요 필드:

```python
entry.title           # 기사 제목
entry.link            # 기사 URL
entry.published       # 발행 시각 (RFC 2822 형식)
entry.published_parsed # 발행 시각 (time.struct_time)
entry.summary         # 기사 요약
entry.source.title    # 뉴스 출처 (예: Reuters, Bloomberg)
entry.id              # 고유 ID (URL과 동일한 경우 많음)
```

---

## 7. 웹 브라우저에서 직접 사용하기

### RSS 피드 URL을 브라우저에서 확인
1. 아래 URL을 브라우저 주소창에 붙여넣기:
   ```
   https://news.google.com/rss/search?q=%22AI+training%22+lawsuit+copyright+when%3A3d&hl=en-US&gl=US&ceid=US:en
   ```
2. XML 형식의 뉴스 피드가 표시됨
3. RSS 리더 앱(Feedly, Inoreader 등)에 구독 URL로 추가 가능

### 브라우저에서 RSS 구독 확인
- **Chrome**: RSS Feed Reader 확장 프로그램 설치 후 사용
- **Firefox**: Live Bookmarks 또는 Feedbro 확장 프로그램
- **Feedly**: https://feedly.com → 검색창에 RSS URL 붙여넣기

---

## 8. 주의사항 및 한계

| 항목 | 내용 |
|------|------|
| **공식 지원** | Google의 공식 API가 아님 — 갑작스러운 형식 변경 가능 |
| **기사 수 제한** | 일반적으로 최대 100개 항목 반환 |
| **중복 기사** | 동일 기사가 여러 검색어로 중복 수집될 수 있음 |
| **링크 형식** | Google이 기사 URL을 직접 제공하지 않고 리디렉션 URL 사용 |
| **속도 제한** | 과도한 요청 시 일시적 차단 가능 |

---

## 9. 이 프로젝트의 쿼리 목록 ([`src/queries.py`](../src/queries.py))

```python
NEWS_QUERIES = [
    '("AI training" OR "model training" OR LLM) (lawsuit OR sued OR litigation) '
    '(copyright OR pirated OR unauthorized OR "shadow library" OR scraping) when:3d',

    '(Anthropic OR OpenAI OR Google OR Meta OR "Snap Inc" OR "Perplexity AI") '
    '(lawsuit OR sued) (training data OR dataset OR copyright OR DMCA) when:3d',

    '("DMCA" OR "copyright infringement") ("AI model" OR "AI training" OR "training data") when:3d',

    '("AI data contract" OR "AI 데이터 계약" OR "data licensing agreement") when:3d',
]
```

---

## 10. 관련 도구 및 참고 자료

| 도구/링크 | 설명 |
|-----------|------|
| [Feedly](https://feedly.com) | RSS 리더 — 피드 구독 및 관리 |
| [feedparser 공식 문서](https://feedparser.readthedocs.io/) | Python RSS 파싱 라이브러리 |
| [crontab.guru](https://crontab.guru/) | cron 표현식 생성기 (GitHub Actions 스케줄링) |
| [Google News](https://news.google.com) | Google 뉴스 웹 인터페이스 |
