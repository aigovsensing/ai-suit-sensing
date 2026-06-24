# ⚖️ CourtListener 사용 가이드

> **대상**: CourtListener 웹사이트 및 REST API v4를 활용하여 미국 연방법원 소송 데이터를 수집하는 방법을 학습합니다.  
> **관련 파일**: [`src/courtlistener.py`](../src/courtlistener.py), [`src/queries.py`](../src/queries.py)

---

## 1. CourtListener란?

[CourtListener](https://www.courtlistener.com)는 **Free Law Project**가 운영하는 무료 공개 법률 데이터 플랫폼입니다.

- 미국 연방법원 및 주 법원의 판결문, 도켓(Docket), 소송 문서를 무료 제공
- RECAP 아카이브(PACER 문서 공개 저장소)와 통합
- REST API v4를 통해 프로그래밍 방식으로 데이터 접근 가능
- 웹 검색 인터페이스와 이메일 알림 기능 제공

### 주요 데이터 유형
| 데이터 | 설명 |
|--------|------|
| **Opinions (판결문)** | 법원이 작성한 판결 전문 |
| **Dockets (도켓)** | 소송 사건의 전체 기록 목록 |
| **RECAP Documents** | PACER에서 업로드된 소송 문서 PDF |
| **Oral Arguments** | 구두 변론 오디오 파일 |
| **Judges** | 판사 약력 및 임명 정보 |

---

## 2. 웹 브라우저로 사용하기

### 2-1. 기본 검색

1. [https://www.courtlistener.com](https://www.courtlistener.com) 접속
2. 검색창에 키워드 입력 (예: `OpenAI copyright training data`)
3. 검색 유형 선택:
   - **Opinions**: 판결문 검색
   - **RECAP Documents**: PACER 문서 검색 ← **이 프로젝트에서 주로 사용**
   - **Oral Arguments**: 구두 변론 검색
   - **People**: 판사 검색

### 2-2. 검색 연산자 (Search Syntax)

```
# 정확한 구문 검색
"AI training data"

# 불리언 AND/OR
"AI training" AND copyright
OpenAI OR Anthropic OR Google

# 제외
"AI training" -patent

# 필드 검색
caseName:"OpenAI"
court:ca9                    # 제9 항소 법원
dateFiled:[2024-01-01 TO *]  # 2024년 이후 소송

# 조합
document_type:"PACER Document" "AI training" copyright
```

### 2-3. RECAP Document 검색 (이 프로젝트 핵심)

**웹 브라우저 검색 절차**:
1. 검색 유형을 **"RECAP Documents"** 선택
2. 쿼리 예시:
   ```
   (short_description:complaint) ("AI training" OR "training data") (copyright OR DMCA)
   ```
3. 결과에서 **"Complaint"** 항목 클릭 → PDF 다운로드 가능

---

## 3. REST API v4 사용하기

### 3-1. API 베이스 URL
```
https://www.courtlistener.com/api/rest/v4/
```

### 3-2. 인증 (Authentication)

**Token 기반 인증 (권장)**:
1. [https://www.courtlistener.com/sign-in/](https://www.courtlistener.com/sign-in/) 에서 계정 생성
2. [https://www.courtlistener.com/api/rest/v4/](https://www.courtlistener.com/api/rest/v4/) 접속 후 Token 발급
3. 요청 헤더에 포함:
   ```
   Authorization: Token YOUR_TOKEN_HERE
   ```

**환경 변수 설정** (이 프로젝트):
```bash
# GitHub Secrets에 등록
COURTLISTENER_TOKEN=your_token_here
```

### 3-3. 주요 엔드포인트

| 엔드포인트 | 설명 |
|-----------|------|
| `/api/rest/v4/search/` | 전체 텍스트 검색 |
| `/api/rest/v4/dockets/` | 도켓(소송 사건) 목록 |
| `/api/rest/v4/dockets/{id}/` | 특정 도켓 상세 조회 |
| `/api/rest/v4/recap-documents/` | RECAP 문서 목록 |
| `/api/rest/v4/opinions/` | 판결문 목록 |
| `/api/rest/v4/courts/` | 법원 목록 |
| `/api/rest/v4/recap-fetch/` | PACER 문서 비동기 다운로드 |

---

## 4. 핵심 API 사용 예시

### 4-1. 소송 문서 검색

```python
import requests

BASE_URL = "https://www.courtlistener.com"
TOKEN = "your_token_here"

headers = {
    "Authorization": f"Token {TOKEN}",
    "Accept": "application/json",
}

# RECAP 문서 검색
params = {
    "q": 'short_description:complaint "AI training" copyright',
    "type": "r",              # r = RECAP documents, ca = cases
    "order_by": "dateFiled desc",
    "page_size": 20,
    "semantic": "true",       # 시맨틱 검색 활성화
}

response = requests.get(
    f"{BASE_URL}/api/rest/v4/search/",
    params=params,
    headers=headers,
    timeout=30,
)
data = response.json()
print(f"총 결과: {data['count']}건")

for item in data["results"]:
    print(f"사건: {item.get('caseName')}")
    print(f"날짜: {item.get('dateFiled')}")
    print(f"도켓 ID: {item.get('docket_id')}")
```

### 4-2. 도켓(사건) 상세 조회

```python
docket_id = 12345678  # 검색 결과에서 얻은 ID

response = requests.get(
    f"{BASE_URL}/api/rest/v4/dockets/{docket_id}/",
    headers=headers,
    timeout=30,
)
docket = response.json()

print(f"사건명: {docket['case_name']}")
print(f"도켓 번호: {docket['docket_number']}")
print(f"법원: {docket['court']}")
print(f"접수일: {docket['date_filed']}")
print(f"담당 판사: {docket.get('assigned_to_str', '미확인')}")
print(f"소송 유형(NOS): {docket.get('nature_of_suit', '미확인')}")
print(f"소송 원인: {docket.get('cause', '미확인')}")
```

### 4-3. RECAP 문서 목록 조회

```python
# 특정 도켓의 모든 문서 조회
response = requests.get(
    f"{BASE_URL}/api/rest/v4/recap-documents/",
    params={"docket": docket_id, "page_size": 100},
    headers=headers,
    timeout=30,
)
docs = response.json()

for doc in docs["results"]:
    desc = doc.get("description", "").lower()
    if "complaint" in desc:
        print(f"Complaint 발견!")
        print(f"  문서 번호: {doc.get('document_number')}")
        print(f"  PDF URL: {doc.get('filepath_local')}")
        print(f"  접수일: {doc.get('date_filed')}")
```

### 4-4. 페이지네이션 처리

```python
all_docs = []
url = f"{BASE_URL}/api/rest/v4/recap-documents/"
params = {"docket": docket_id, "page_size": 100}

while url:
    response = requests.get(url, params=params, headers=headers, timeout=30)
    data = response.json()
    all_docs.extend(data.get("results", []))
    url = data.get("next")      # 다음 페이지 URL (없으면 None)
    params = None               # 두 번째 요청부터는 파라미터 불필요

print(f"총 문서 수: {len(all_docs)}")
```

---

## 5. Nature of Suit (NOS) 코드 안내

소송 유형을 구분하는 코드로, 이 프로젝트에서 AI 저작권 소송 필터링에 활용합니다.

| NOS 코드 | 의미 |
|---------|------|
| **820** | Copyright (저작권) ← **핵심 모니터링 대상** |
| **3820** | Copyright Appeal (저작권 항소) |
| **830** | Patent (특허) |
| **840** | Trademark (상표) |
| **190** | Contract: Other (기타 계약) |
| **410** | Antitrust (독점금지법) |
| **360** | Personal Injury: Other |

### Cause of Action (COA) 코드

| COA 코드 | 의미 |
|---------|------|
| **17:501** | Copyright Infringement (저작권 침해) |
| **17:101** | Copyright Infringement |
| **17:512** | DMCA |
| **17:1201** | DMCA (기술적 보호조치 우회) |
| **35:271** | Patent Infringement |
| **15:1125** | Trademark Infringement (Lanham Act) |

---

## 6. 도켓 URL 구조

CourtListener에서 소송 사건 페이지 URL 형식:

```
https://www.courtlistener.com/docket/{docket_id}/{case-name-slug}/
```

예시:
```
https://www.courtlistener.com/docket/67351709/8a/sa-jamendo-v-nvidia-corporation/
```

**Python으로 slug 생성**:
```python
import re

def slugify_case_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = name.strip("-")
    return name

slug = slugify_case_name("S.A. JAMENDO v. NVIDIA Corporation")
# 결과: "s-a-jamendo-v-nvidia-corporation"
```

---

## 7. 검색 타입(type) 파라미터

| type 값 | 의미 | 용도 |
|---------|------|------|
| `r` | RECAP Documents | 소송 문서 검색 (PDF 포함) |
| `ca` | Cases/Dockets | 사건 단위 검색 |
| `o` | Opinions | 판결문 검색 |
| `oa` | Oral Arguments | 구두 변론 검색 |
| `p` | People/Judges | 판사 검색 |

---

## 8. 이 프로젝트의 검색 쿼리 ([`src/queries.py`](../src/queries.py))

```python
COURTLISTENER_QUERIES = [
    # 1) AI 학습 관련 Complaint 포괄 검색
    'document_type:"PACER Document" '
    '(short_description:complaint OR short_description:"amended complaint" OR short_description:petition) '
    '("AI training" OR "model training" OR "training data" OR dataset OR LLM OR "large language model") '
    '(copyright OR DMCA OR unauthorized OR pirated OR scraping OR "without permission")',

    # 2) 주요 AI 기업 대상 소송
    'document_type:"PACER Document" '
    '(short_description:complaint OR short_description:"amended complaint") '
    '(Anthropic OR OpenAI OR Google OR Meta OR "Snap Inc" OR "Perplexity AI" OR Claude OR Gemini) '
    '("training data" OR "AI training" OR dataset) '
    '(copyright OR DMCA OR unauthorized)',

    # 3) Shadow Library/해적판 데이터 관련
    'document_type:"PACER Document" '
    '(short_description:complaint OR short_description:"amended complaint" OR short_description:petition) '
    '("shadow library" OR LibGen OR "Library Genesis" OR Z-Library OR Books3 OR piracy OR pirated) '
    '("AI training" OR "training data" OR LLM)',
]
```

---

## 9. 알림 기능 (Docket Alerts)

CourtListener는 특정 사건이 업데이트될 때 이메일 알림을 보내는 기능을 제공합니다.

**설정 방법**:
1. CourtListener 로그인
2. 관심 도켓 페이지 방문
3. 우측 사이드바의 **"Get Alerts"** 클릭
4. 이메일 주소 입력 후 구독

---

## 10. 참고 자료

| 링크 | 설명 |
|------|------|
| [CourtListener](https://www.courtlistener.com) | 메인 웹사이트 |
| [API 문서 (Free Law Wiki)](https://github.com/freelawproject/courtlistener/wiki) | REST API v4 공식 문서 |
| [API 브라우저](https://www.courtlistener.com/api/rest/v4/) | 인터랙티브 API 탐색기 |
| [RECAP 아카이브](https://www.courtlistener.com/recap/) | PACER 문서 무료 검색 |
| [Free Law Project](https://free.law) | 운영 기관 |
