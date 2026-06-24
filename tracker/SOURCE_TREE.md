좋아요, 전체 구조를 **트리 형태 + 각 파일 역할 설명**으로 정리해드릴게요.
(업로드해주신 `ai-law-suit-tracker-20260130-main` 기준)

---

# 📁 프로젝트 구조 설명

```text
ai-law-suit-tracker-20260130-main
├── .github/
│   └── workflows/
│       └── hourly.yml
├── .gitignore
├── README.md
├── data/
│   └── known_cases.yml
├── requirements.txt
└── src/
    ├── __init__.py
    ├── complaint_parse.py
    ├── courtlistener.py
    ├── extract.py
    ├── fetch.py
    ├── github_issue.py
    ├── pdf_text.py
    ├── queries.py
    ├── render.py
    ├── run.py
    └── slack.py
```

---

## 🔧 루트 레벨

### `.github/workflows/hourly.yml`

* GitHub Actions 워크플로 파일
* 이 프로젝트를 **1시간마다 자동 실행**
* 실행 내용:

  1. Python 환경 세팅
  2. 의존성 설치
  3. `python -m src.run` 실행
  4. 결과를 GitHub Issue + Slack으로 전송

---

### `README.md`

* 프로젝트 개요 및 사용 방법 설명 문서
* 어떤 데이터를 수집하는지, 어떤 API를 쓰는지, 실행 방법 등이 정리됨

---

### `requirements.txt`

* Python 의존 라이브러리 목록
* 주요 패키지:

  * `requests` → API 호출
  * `feedparser` → 뉴스 RSS 파싱
  * `beautifulsoup4`, `lxml` → HTML 파싱
  * `pypdf` → 소장 PDF 텍스트 추출

---

### `data/known_cases.yml`

* 이미 알려진/수동 관리되는 소송 케이스 목록
* 자동 수집 결과와 **중복 방지** 또는 **보강 정보 제공**에 사용될 수 있음

---

## 🧠 핵심 로직: `src/` 폴더

여기가 실제 시스템의 두뇌입니다.

---

### `run.py` ⭐ **엔트리포인트 (가장 중요)**

* 전체 파이프라인을 오케스트레이션하는 메인 모듈
* 하는 일:

  1. 최근 3일 날짜 계산
  2. 뉴스 + CourtListener 데이터 수집
  3. RECAP 문서 분석
  4. 결과 테이블 생성
  5. GitHub Issue 업데이트
  6. Slack 메시지 전송

👉 **시스템의 시작점 = `python -m src.run`**

---

### `queries.py`

* CourtListener 검색에 사용할 **검색 쿼리(키워드)** 정의
* 예: AI training, dataset, scraping, copyright 등
* “어떤 소송을 찾을지”를 결정하는 필터 역할

---

### `courtlistener.py`

* CourtListener API 연동 핵심 모듈
* 기능:

  * 사건(도켓) 검색
  * RECAP 문서 목록 조회
  * Complaint 우선 선택
  * (추가된 기능) Complaint 없으면 Motion/Order 등 fallback 문서 선택

---

### `pdf_text.py`

* RECAP에서 받은 **PDF 소장 파일을 텍스트로 변환**
* `pypdf` 사용
* 이후 소송 이유, 핵심 문장 추출의 기반 데이터 제공

---

### `complaint_parse.py`

* 소장 텍스트에서 구조화 정보 추출
* 예:

  * 원고/피고 추정
  * 청구 원인 키워드
  * AI 학습 관련 문장

---

### `extract.py`

* 뉴스/문서 텍스트에서

  * 사건 제목
  * 소송 이유
  * 날짜
    등을 뽑아내는 **정보 추출 로직 모음**

---

### `fetch.py`

* 뉴스 RSS 및 웹 페이지 가져오는 모듈
* 언론 기사 기반 소송 정보 수집 담당

---

### `render.py`

* 최종 결과를 **Markdown 테이블 형태로 변환**
* GitHub Issue에 올릴 본문 생성

---

### `github_issue.py`

* GitHub API 연동 모듈
* 기능:

  * 날짜별 이슈 찾기 또는 생성
  * 댓글 추가
  * 이전 날짜 이슈 자동 Close
  * Close 전에 "다음 리포트 링크" 코멘트 작성

---

### `slack.py`

* Slack Webhook으로 요약 메시지 전송
* 메시지 예:

  * 뉴스 몇 건
  * RECAP Complaint 몇 건
  * Fallback 문서 몇 건
  * 이슈 번호 링크

---

### `__init__.py`

* Python 패키지 인식용 (특별한 로직 없음)

---

# 🧭 전체 흐름 요약

```text
GitHub Actions (hourly.yml)
        ↓
python -m src.run
        ↓
[queries] 검색 키워드 준비
        ↓
[courtlistener] 소송 + RECAP 문서 수집
        ↓
[pdf_text] PDF → 텍스트
        ↓
[complaint_parse / extract] 정보 구조화
        ↓
[fetch] 뉴스 보강
        ↓
[render] Markdown 테이블 생성
        ↓
[github_issue] GitHub 이슈 업데이트 + 이전 이슈 닫기
        ↓
[slack] 요약 메시지 전송
```

---

원하시면 다음 단계로
📌 **“run.py 기준 실제 호출 순서 다이어그램”** 도 그려드릴 수 있어요.
