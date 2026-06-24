# TBA-Analyzer 구현 계획서 (Implementation Plan)

> **TBA-Analyzer** = *Triage & Bridge Analyzer*
> `tracker`(센싱)와 `dashboard`(시각화) 사이의 **수동 분석/정리 단계를 자동화**하되,
> CSV 반영 전에 **사람이 검토(accept/reject)**하는 *Human-in-the-Loop* 분석기.

---

## 1. 배경 & 문제 정의

### 1.1 현재 워크플로우 (수동)
```
tracker (자동 센싱)
   └─▶ GitHub Issue 리포트 (label: ai-lawsuit-monitor, 일자별 이슈 + 누적 댓글)
            │
            ▼  ← ★ 여기가 사람이 수동으로 하는 구간 (자동화 대상)
   사람이 이슈 내용을 읽고 신규/수정/업데이트 소송을 직접 분석·정리
            │
            ▼
   dashboard/data/aisuit_YYYYMMDD[_HHMM].csv 로 저장
            │
            ▼
   dashboard (CSV 기반 시각화/조회)
```

### 1.2 문제점
- 이슈 내용을 사람이 일일이 읽고 **신규 소송 추가 / 기존 소송 업데이트**를 판단해야 함 → 시간·실수 비용.
- 같은 소송이 여러 날 반복 보고되므로 **기존 CSV와 대조(diff)**가 매번 필요.
- 소송 데이터는 법적 민감 정보이므로 **잘못된 자동 반영은 위험** → 완전 자동화는 부적절.

### 1.3 목표
1. 이슈 내용을 분석해 **구조화된 소송 레코드**로 추출.
2. 기존 `dashboard/data/*.csv`(정본)와 **대조**하여 `NEW` / `UPDATE` / `UNCHANGED` 분류.
3. **변경 제안(changeset)**을 생성하되 **곧바로 CSV에 반영하지 않음**.
4. 사람이 제안을 **검토 → accept하면 자동 반영, reject하면 폐기**.
5. (장기) 신뢰도가 쌓이면 일부 단계를 점진적으로 자동 승인.

> **핵심 원칙**: *"제안은 자동, 반영은 승인 후."* 소송 데이터의 정확성이 최우선이므로 기본값은 항상 사람 검토.

---

## 2. 데이터 모델 (정본 CSV 스키마)

분석기의 출력은 dashboard가 읽는 정본 CSV 포맷과 **완전히 동일**해야 한다.
(`dashboard/collector/builder.py: build_from_csv()` 가 기준이며, 1~2행은 메타, **3행이 헤더**.)

| # | 컬럼 | 역할 | 식별키 |
|---|------|------|:---:|
| 1 | `No` | 행 번호 | |
| 2 | `System ID` | 내부 고유 ID | ◎ (1순위) |
| 3 | `진행현황` | 상태(소 제기됨/진행중/종결 등) | |
| 4 | `소송제목 (원고 v. 피고)*` | 사건명 | ○ |
| 5 | `소송번호*` | 도켓번호 (예: `5:26-cv-06206`) | ◎ (2순위) |
| 6 | `소송제기일*` | 제소일 | ○ |
| 7 | `원고` | | |
| 8 | `피고` | | |
| 9 | `대상 데이터` | | |
| 10 | `대상 제품` | | |
| 11 | `소송이유` | | |
| 12 | `법원` | | |
| 13 | `국가*` | | |
| 14 | `소송금액 (USD)` | | |
| 15 | `개요 및 배경 (By Gauss)` | LLM 요약 | |
| 16 | `Tracker(업로드 시 제외)` | 원본 이슈/소스 URL | |
| 17 | `관련 주소 (초기)(업로드 시 제외)` | | |
| 18 | `Last Update(업로드 시 제외)` | 최종 갱신 시각 | |
| 19 | `진행결과` | | |
| 20 | `히스토리(업로드 시 제외)` | 변경 이력 누적 | |
| 21 | `변호사(원고)` | | |
| 22 | `변호사(피고)` | | |
| 23 | `비고(업로드 시 제외)` | | |

**식별 전략 (matching key)** — 동일 소송 판별 우선순위:
1. **`소송번호*`(도켓번호) 정규화 비교** — 가장 신뢰도 높음. (대소문자/공백/법원 접두 제거 후 비교)
2. `System ID` 일치.
3. (도켓번호 없을 때) `원고`+`피고`+`소송제기일*` 조합 또는 `소송제목` **퍼지 매칭**(rapidfuzz, 임계값 설정).

> `tracker/data/known_cases.yml` 의 enrich 규칙(도켓번호↔사건명 보강)을 분석기도 재사용하여 매칭 정확도를 높인다.

---

## 3. 아키텍처

```
tba-analyzer/
├── implementation-plan.md      # (본 문서)
├── README.md                   # 사용법
├── requirements.txt            # google-generativeai, pandas, rapidfuzz, PyYAML, requests
├── config.yaml                 # 라벨/임계값/경로/모델명 등 설정
├── src/
│   ├── __init__.py
│   ├── run.py                  # 엔트리포인트 (CLI / Actions)
│   ├── ingest.py               # GitHub Issue + 댓글 수집 (tracker가 만든 이슈)
│   ├── extract.py              # 이슈 텍스트 → 구조화 레코드 (Gemini + 규칙 파서)
│   ├── csv_store.py            # 정본 CSV 로드/저장 (3행 헤더 포맷 준수)
│   ├── matcher.py              # 도켓/퍼지 매칭으로 NEW/UPDATE/UNCHANGED 분류
│   ├── diff.py                 # 필드 단위 변경 계산 + 히스토리 패치 생성
│   ├── changeset.py            # 변경 제안(proposal) 객체 직렬화/역직렬화
│   ├── apply.py                # accept된 changeset을 새 CSV 버전으로 반영
│   └── review/                 # 사람 검토 인터페이스 (3절 4.3 참조)
├── proposals/                  # 생성된 변경 제안 (검토 대기) — *.json
└── tests/
    └── fixtures/               # 샘플 이슈 본문 + 기대 레코드
```

### 3.1 파이프라인 단계

```
[1] ingest    GitHub Issue/댓글 수집 ──┐
                                       ▼
[2] extract   LLM+규칙으로 구조화 레코드 추출 (소송별 dict)
                                       ▼
[3] match     최신 정본 CSV 로드 → 도켓/퍼지 매칭 → NEW/UPDATE/UNCHANGED
                                       ▼
[4] diff      UPDATE 건은 필드별 before/after 계산, 히스토리 패치 생성
                                       ▼
[5] changeset 변경 제안(proposal.json) 생성 — ★ 여기까지 자동, CSV 미반영
                                       ▼
[6] review    ★ 사람 검토: 항목별 accept / reject  (Human-in-the-Loop)
                                       ▼
[7] apply     accept 항목만 새 CSV 버전(aisuit_YYYYMMDD_HHMM.csv)으로 반영
```

### 3.2 변경 제안(Changeset) 데이터 구조 (예시)

```jsonc
{
  "generated_at": "2026-06-24T10:00:00Z",
  "source_issue": "https://github.com/aigovsensing/ai-suit-sensing/issues/123",
  "base_csv": "dashboard/data/aisuit_20260624_0947.csv",
  "proposals": [
    {
      "id": "p1",
      "type": "NEW",
      "match_key": "5:26-cv-06206",
      "confidence": 0.97,
      "record": { /* 23개 컬럼 값 */ },
      "evidence": "이슈 댓글에서 추출한 근거 텍스트 발췌",
      "decision": "pending"          // pending | accepted | rejected
    },
    {
      "id": "p2",
      "type": "UPDATE",
      "match_key": "3:24-cv-05417",
      "target_system_id": "5001369427",
      "confidence": 0.88,
      "field_changes": [
        { "column": "진행현황", "before": "소 제기됨", "after": "진행중" },
        { "column": "진행결과", "before": "", "after": "약식판결 신청 기각" }
      ],
      "history_append": "[2026-06-24] 진행현황: 소 제기됨 → 진행중",
      "evidence": "...",
      "decision": "pending"
    }
  ]
}
```

---

## 4. 사람 검토(Human-in-the-Loop) 설계 — 핵심

자동화하되 **CSV 반영 직전에 반드시 사람이 accept/reject**. 3가지 방식을 제안하며, **방식 A(GitHub PR)**를 권장한다.

### 4.1 (권장) 방식 A — GitHub Pull Request 기반 검토
- 분석기가 새 CSV(또는 패치)를 브랜치에 커밋하고 **PR을 자동 생성**.
- PR 본문에 사람이 읽기 쉬운 **변경 요약 표**(NEW n건 / UPDATE m건, 항목별 before→after)를 첨부.
- **검토 = PR 리뷰**: 사람이 PR diff를 보고
  - **accept → PR merge** (= 새 CSV 정본 반영, 자동),
  - **reject → PR close** (= 미반영).
- 항목 단위 거부는 PR에서 해당 행 수정/커밋으로 처리하거나, 제안을 분리 생성.
- **장점**: 감사 추적(audit trail)·이력·되돌리기(revert)가 git에 그대로 남고, 별도 UI 불필요. 모노레포 + GitHub Actions와 자연스럽게 결합.

### 4.2 방식 B — CLI 대화형 검토
```bash
python -m src.run review proposals/2026-06-24.json
# 각 제안을 출력하고 [a]ccept / [r]eject / [s]kip / [e]dit 입력 받음
```
- 오프라인/로컬에서 빠르게 검토. 결과를 `decision` 필드에 기록 후 `apply` 단계로.

### 4.3 방식 C — 경량 웹 검토 UI (dashboard에 통합)
- `dashboard/backend`에 `/review` 엔드포인트를 추가하여 대기 중 제안을 카드로 표시, 버튼으로 accept/reject.
- 비개발자(법무/분석 담당)도 사용 가능. 단, 구현 비용이 가장 큼.

> **단계별 채택**: 1차 출시 = **방식 A(PR)** + 방식 B(CLI) 보조 → 안정화 후 방식 C(웹 UI) 검토.

### 4.4 신뢰도 기반 점진적 자동화 (장기)
- 각 제안에 `confidence` 점수 부여.
- 초기: **모든 제안 사람 검토**(자동 승인 0%).
- 누적 검토 결과로 정확도 측정 → 예: "도켓번호 완전 일치 + 신규 + confidence ≥ 0.95"처럼 **저위험 패턴만 자동 승인**으로 점진 확대. 나머지는 계속 사람 검토.
- 자동 승인된 건도 PR/커밋 이력으로 사후 감사 가능.

---

## 5. 반영(apply) 규칙

- **NEW**: 정본 CSV에 새 행 추가. `No`는 max+1, `System ID`는 신규 발급(또는 도켓번호 기반 결정적 생성), `Last Update`=현재 시각, `히스토리`에 최초 등록 기록.
- **UPDATE**: 기존 행을 식별키로 찾아 변경 필드만 갱신.
  - `히스토리(업로드 시 제외)` 컬럼에 `[날짜] 컬럼: before → after` 누적 (덮어쓰지 않고 append).
  - `Last Update` 갱신.
- **출력**: 기존 파일을 덮어쓰지 않고 **새 타임스탬프 파일**(`aisuit_YYYYMMDD_HHMM.csv`)로 저장 → 자연스러운 버전 관리. dashboard는 최신 파일을 자동 감지.
- **포맷 보존**: 1행 제목, 2행 추출기간, 3행 헤더, `(업로드 시 제외)` 컬럼 유지. `csv_store.py`가 round-trip 무결성 테스트로 보장.

---

## 6. 기술 스택

| 영역 | 선택 | 비고 |
|------|------|------|
| 언어 | Python 3.11 | tracker와 동일 |
| LLM 추출 | `google-generativeai`(Gemini) | tracker가 이미 사용, 키 재사용 |
| 표 처리 | `pandas` | dashboard builder와 동일 |
| 퍼지 매칭 | `rapidfuzz` | 사건명 유사도 |
| 설정/규칙 | `PyYAML` | `config.yaml`, `known_cases.yml` 재사용 |
| GitHub 연동 | `requests` (GitHub REST) 또는 `gh` CLI | 이슈 수집 / PR 생성 |
| 실행 | GitHub Actions + CLI | 4.1 / 4.2 |

> **LLM 추출의 안전장치**: 프롬프트로 23개 컬럼 스키마를 강제하고, JSON 스키마 검증 + 도켓번호 정규식 검증을 거쳐 환각(hallucination)을 차단. 검증 실패 레코드는 `confidence`를 낮춰 반드시 사람 검토로 보냄.

---

## 7. 단계별 로드맵

| 단계 | 산출물 | 사람 개입 |
|------|--------|-----------|
| **P0. 골격** | 폴더/설정/CSV round-trip 로더(`csv_store.py`) + 테스트 | - |
| **P1. 추출** | `ingest.py` + `extract.py` (이슈 → 레코드), fixture 테스트 | - |
| **P2. 대조** | `matcher.py` + `diff.py` (NEW/UPDATE 분류, 변경 계산) | - |
| **P3. 제안** | `changeset.py` (proposal.json 생성) — **CSV 미반영** | - |
| **P4. 검토** | 방식 B(CLI) 검토 + `apply.py` (accept만 반영) | **필수** |
| **P5. PR 자동화** | 방식 A: Actions가 PR 생성, merge=반영 | **필수(PR 리뷰)** |
| **P6. (선택) 웹 UI** | 방식 C: dashboard `/review` | 필수 |
| **P7. (장기) 점진 자동승인** | 신뢰도 기반 저위험 자동 승인 | 축소 |

---

## 8. 리스크 & 대응

| 리스크 | 대응 |
|--------|------|
| LLM 추출 오류/환각 | 스키마·정규식 검증, 낮은 confidence는 사람 검토 강제, 근거(evidence) 첨부 |
| 잘못된 매칭으로 엉뚱한 행 덮어씀 | 도켓번호 정규화 1순위, 퍼지 매칭은 임계값+사람 확인, UPDATE는 항상 before/after 표시 |
| 정본 CSV 포맷 손상 | 덮어쓰기 금지(새 버전 파일), round-trip 무결성 테스트, git 이력으로 revert |
| 자동 반영의 법적 위험 | **기본값=사람 검토**, 자동 승인은 저위험 패턴으로 점진 도입 |
| 중복 보고(여러 날) | `UNCHANGED`로 분류해 제안에서 제외, tracker dedup 로직 참고 |

---

## 9. 다음 액션 (착수 시)
1. `config.yaml` + `csv_store.py`(round-trip 테스트 포함)부터 구현 — 정본 포맷 보존이 토대.
2. 실제 이슈 1~2건을 fixture로 확보해 `extract.py` 프롬프트 튜닝.
3. `matcher.py`로 최신 CSV 대조 → 첫 `proposal.json` 생성까지 E2E 확인.
4. CLI 검토(방식 B)로 사람 accept/reject → `apply.py` 반영 검증.
5. 안정화 후 GitHub Actions PR 자동화(방식 A) 연결.
```
