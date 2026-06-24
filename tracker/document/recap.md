# 🗂️ RECAP & PACER 사용 가이드

> **대상**: PACER(미국 연방법원 전자기록 시스템)와 RECAP 브라우저 확장 프로그램의 사용법 및 이 프로젝트와의 연동 방법을 학습합니다.  
> **관련 파일**: [`src/courtlistener.py`](../src/courtlistener.py)

---

## 1. PACER (Public Access to Court Electronic Records)

### PACER란?
PACER는 미국 사법부(Administrative Office of the U.S. Courts)가 운영하는 **유료** 연방법원 전자기록 접근 시스템입니다.

- **웹사이트**: https://pacer.uscourts.gov
- **대상**: 미국 연방지방법원, 항소법원, 파산법원의 모든 공개 소송 기록
- **비용**: 페이지당 $0.10 (문서당 최대 $3.00 상한)
  - 분기 총 사용액이 $30 미만이면 **무료**
- **이용 가능**: 전 세계 누구나 계정 생성 가능

### PACER 계정 생성 방법

1. [https://pacer.uscourts.gov](https://pacer.uscourts.gov) 접속
2. **"Register for an Account"** 클릭
3. **"Register for a PACER Account"** 선택
4. 개인 정보 입력 (이름, 이메일, 주소 등)
5. 사용자명/비밀번호 설정
6. 계정 활성화까지 **24~48시간** 소요

> ⚠️ **중요**: PACER 비밀번호는 **180일마다 갱신** 필요. MFA(다단계 인증) 활성화 시 API 자동화에 문제 발생할 수 있음.

---

## 2. PACER 사용 방법 (브라우저)

### 2-1. 사건 검색

**방법 1 - 법원을 알고 있는 경우**:
1. PACER 로그인
2. 해당 법원 선택 (예: N.D. Cal. = 캘리포니아 북부지방법원)
3. **"Query"** 메뉴 → 사건 번호 또는 당사자명 입력

**방법 2 - 법원을 모르는 경우 (PACER Case Locator)**:
1. https://pcl.uscourts.gov 접속
2. 사건명 또는 당사자명으로 전국 법원 검색
3. 결과에서 해당 법원 및 사건 번호 확인

### 2-2. 도켓(사건 기록) 조회

1. 사건 검색 후 **"Docket Report"** 선택
2. 날짜 범위 설정 (선택사항)
3. 도켓 보고서 생성 → 모든 문서 목록 표시
4. 문서 번호 옆 링크 클릭 → PDF 뷰어 열림

### 2-3. 도켓 번호 형식

```
1:24-cv-01234      → 지방법원 민사 사건
                    (법원구:연도-유형-일련번호)
  유형:
  cv = Civil (민사)
  cr = Criminal (형사)
  bk = Bankruptcy (파산)
  mc = Miscellaneous (기타)
```

예시:
```
1:23-cv-11195-SHS   → SDNY (뉴욕 남부지방법원), 2023년 민사 11195번
                      SHS = 담당 판사 이니셜 (Sidney H. Stein)
```

---

## 3. RECAP 브라우저 확장 프로그램

### RECAP이란?
RECAP은 Free Law Project가 개발한 **무료 브라우저 확장 프로그램**으로, PACER를 사용하면서 이미 공개된 문서를 무료로 얻거나 새로 구매한 문서를 자동으로 공유하는 도구입니다.

> **이름의 의미**: "RECAP" = "PACER" 거꾸로 = PACER를 뒤집어 개방한다는 의미

### 작동 원리

```
[사용자] → [PACER 검색]
              ↓
[RECAP 확장] → RECAP 아카이브 확인
              ↓
       문서 존재?
      ┌──YES──┐     ┌──NO──┐
      ↓              ↓
  무료 링크 제공    PACER에서 유료 구매
                      ↓
               자동으로 RECAP 아카이브에 업로드
                      ↓
               다른 사용자에게 무료 제공
```

### 설치 방법

| 브라우저 | 링크 |
|---------|------|
| Chrome | [Chrome 웹 스토어](https://chrome.google.com/webstore/detail/recap/oiillickanjlaeghobeeknbddaonmjnc) |
| Firefox | [Firefox Add-ons](https://addons.mozilla.org/en-US/firefox/addon/recap-extension/) |
| Safari | [Mac App Store](https://apps.apple.com/app/recap/id1591762882) |

### 사용 방법

1. **브라우저에 RECAP 확장 설치**
2. **PACER에 평소처럼 로그인**
3. 문서 조회 시 RECAP이 자동으로:
   - 아카이브에 이미 있는 문서 → 무료 다운로드 링크 표시 🆓
   - 없는 문서 → PACER에서 구매 후 자동 업로드 ⬆️
4. **별도 설정 없이 백그라운드에서 작동**

### RECAP의 특징

| 특징 | 설명 |
|------|------|
| **비용 절감** | 이미 아카이브에 있는 문서는 $0 |
| **자동 공유** | 새 문서 구매 시 자동으로 공개 아카이브에 업로드 |
| **익명성** | 사용자 개인 정보 수집 없음 |
| **봉인 문서 제외** | Sealed/restricted 문서는 자동 업로드 안 함 |
| **법원 제한 없음** | 모든 PACER 법원에서 작동 |

---

## 4. RECAP 아카이브 (CourtListener)

RECAP 확장 프로그램이 수집한 모든 문서는 **CourtListener RECAP Archive**에 저장됩니다.

### 웹에서 RECAP 아카이브 검색

1. [https://www.courtlistener.com/recap/](https://www.courtlistener.com/recap/) 접속
2. 사건명, 도켓 번호, 키워드로 검색
3. 무료로 PDF 다운로드

### RECAP 문서 저장 경로

```
https://storage.courtlistener.com/recap/{filename}.pdf
```

예시:
```
https://storage.courtlistener.com/recap/gov.uscourts.cand.419924/gov.uscourts.cand.419924.1.0.pdf
```

경로 구조:
```
gov.uscourts.{court_code}.{docket_id}/{court_code}.{docket_id}.{doc_no}.{attachment_no}.pdf
```

---

## 5. 이 프로젝트에서 RECAP 활용 방식

### API를 통한 RECAP 문서 조회

```python
from src.courtlistener import (
    search_recent_documents,
    build_complaint_documents_from_hits,
    build_case_summaries_from_hits,
)

# 1단계: 최근 소송 문서 검색
hits = search_recent_documents(
    query='"AI training" copyright complaint',
    days=3,
    max_results=20
)

# 2단계: Complaint 문서 수집 (PDF 포함)
documents = build_complaint_documents_from_hits(hits, days=3)

for doc in documents:
    print(f"사건명: {doc.case_name}")
    print(f"법원: {doc.court}")
    print(f"PDF URL: {doc.pdf_url}")
    print(f"AI 관련 발췌: {doc.extracted_ai_snippet}")

# 3단계: 사건 요약 정보 수집
cases = build_case_summaries_from_hits(hits)

for case in cases:
    print(f"사건명: {case.case_name}")
    print(f"NOS: {case.nature_of_suit}")     # Nature of Suit
    print(f"원고: {case.plaintiff}")
    print(f"피고: {case.defendant}")
    print(f"상태: {case.status}")
```

### RECAP → HTML Fallback 전략

이 프로젝트는 RECAP API에서 문서를 찾지 못할 경우 **HTML Fallback**을 사용합니다:

```python
# courtlistener.py 내부 로직
if not docs:  # RECAP 문서 없음
    # CourtListener 도켓 웹 페이지에서 PDF 링크 직접 추출
    html_pdf_url = _extract_first_pdf_from_docket_html(docket_id)
```

---

## 6. PACER 법원 코드 (Court IDs)

CourtListener에서 법원을 필터링할 때 사용하는 코드:

### 주요 연방 지방법원
| 코드 | 법원명 |
|------|-------|
| `cand` | N.D. Cal. (캘리포니아 북부 — 실리콘밸리) |
| `cacd` | C.D. Cal. (캘리포니아 중부 — LA) |
| `nysd` | S.D.N.Y. (뉴욕 남부) |
| `nynd` | N.D.N.Y. (뉴욕 북부) |
| `dcd` | D.D.C. (워싱턴 D.C.) |
| `txnd` | N.D. Tex. (텍사스 북부) |
| `ilnd` | N.D. Ill. (일리노이 북부 — 시카고) |

### 연방 항소법원
| 코드 | 법원명 |
|------|-------|
| `ca9` | 제9 항소법원 (서부) |
| `ca2` | 제2 항소법원 (뉴욕/동부) |
| `cafc` | Federal Circuit (특허 전문) |
| `scotus` | 대법원 |

---

## 7. PDF 텍스트 추출 (이 프로젝트)

```python
# src/pdf_text.py
from pypdf import PdfReader
import requests
from io import BytesIO

def extract_pdf_text(pdf_url: str, max_chars: int = 4000) -> str:
    """RECAP PDF에서 텍스트 추출 (앞부분 max_chars 글자만)"""
    try:
        response = requests.get(pdf_url, timeout=30)
        reader = PdfReader(BytesIO(response.content))

        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
            if len(text) >= max_chars:
                break

        return text[:max_chars]
    except Exception as e:
        return ""
```

**PDF 앞부분만 추출하는 이유**:
- Complaint 문서는 초반 5페이지에 핵심 주장(AI 학습 관련) 포함
- 4,000~4,500자 ≈ 약 2~3페이지 분량
- 전체 PDF 다운로드 대비 비용/시간 절감

---

## 8. Docket Alert 설정 (이메일 알림)

CourtListener에서 특정 사건 업데이트 시 이메일 알림 받기:

1. [CourtListener](https://www.courtlistener.com) 로그인
2. 관심 사건 도켓 페이지 방문
3. 우측 **"Get Alerts"** → **"Create Alert"** 클릭
4. 알림 빈도 설정: Real-time / Daily / Weekly
5. 이메일 자동 발송

---

## 9. 참고 자료

| 링크 | 설명 |
|------|------|
| [PACER 공식 사이트](https://pacer.uscourts.gov) | 계정 생성 및 법원 접속 |
| [PACER Case Locator](https://pcl.uscourts.gov) | 전국 사건 통합 검색 |
| [RECAP 프로젝트](https://free.law/recap/) | 브라우저 확장 설치 |
| [RECAP 아카이브](https://www.courtlistener.com/recap/) | 무료 PACER 문서 검색 |
| [CourtListener API](https://www.courtlistener.com/api/rest/v4/) | REST API 탐색기 |
| [Free Law Project](https://free.law) | RECAP/CourtListener 운영 기관 |
