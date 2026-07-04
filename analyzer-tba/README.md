# Analyzer-TBA

`tracker`(센싱)와 `dashboard`(시각화) 사이의 **수동 분석/정리 단계를 자동화**하는 분석기.
GitHub Issue로 보고된 소송 내용을 분석해 정본 CSV(`dashboard/data/*.csv`)와 대조하고,
**신규/업데이트 변경 제안**을 생성한다.

> **핵심 원칙**: *제안은 자동, 반영은 사람 승인 후.*
> 소송 데이터는 법적 민감 정보이므로 CSV 반영 전에 반드시 사람이 검토(accept/reject)한다.

설계 배경/로드맵은 [implementation-plan.md](./implementation-plan.md) 참고.

## 파이프라인

```
ingest(이슈 수집) → extract(LLM 구조화) → match(기존 CSV 대조)
→ diff(변경 계산) → changeset(제안 생성, CSV 미반영)
→ review(사람 accept/reject) → apply(승인분만 새 CSV 버전으로 반영)
```

## 설치

```bash
cd analyzer-tba
pip install -r requirements.txt
export GEMINI_API_KEY=...   # LLM 추출용
export GITHUB_TOKEN=...      # 이슈 수집용
```

## 사용법

### 1) 분석 → 제안 생성 (정본 CSV 변경 없음)
```bash
# GitHub 이슈에서 수집
python -m src.run analyze --limit 3 --write-candidate

# 로컬 이슈 텍스트 파일로(테스트)
python -m src.run analyze --issue-file path/to/issue.md --write-candidate

# 추출 결과를 직접 주입(LLM 생략, 재현/테스트)
python -m src.run analyze --extracted-json tests/fixtures/sample_extracted.json --write-candidate
```
산출물:
- `proposals/changeset_<stamp>.json` — 변경 제안(모든 decision=pending)
- `proposals/changeset_<stamp>.md` — 사람이 읽는 변경 요약(PR 본문용)
- `dashboard/data/aisuit_<stamp>.csv` — 후보 CSV(`--write-candidate` 시)

### 2-A) 검토 방식 A — GitHub PR (권장)
GitHub Actions(`.github/workflows/analyzer-tba.yml`)가 위 분석을 실행하고,
후보 CSV를 브랜치에 커밋해 **PR을 자동 생성**한다.
- **merge** → 정본 CSV 반영(accept)
- **close** → 미반영(reject)
- 일부만 반영하려면 PR 브랜치의 CSV를 직접 수정 후 머지.

### 2-B) 검토 방식 B — CLI (보조)
```bash
python -m src.run review proposals/changeset_<stamp>.json   # a/r/s 로 항목별 결정
python -m src.run apply  proposals/changeset_<stamp>.json   # accept된 것만 반영
```

## 매칭 규칙 (동일 소송 판별)
1. **`소송번호*`(도켓번호) 정규화 비교** — confidence 0.97
2. `System ID` 일치 — 0.95
3. 사건명 **퍼지 매칭**(rapidfuzz, 임계값 `config.yaml: matching.fuzzy_threshold`)

UPDATE 시 빈 값은 덮어쓰지 않으며(센싱 누락 보호), 변경 이력은 `히스토리` 컬럼에 누적된다.
정본 CSV는 덮어쓰지 않고 항상 **새 타임스탬프 파일**로 저장한다(git 이력 = 감사 추적).

## 테스트
```bash
python -m tests.test_csv_store   # 정본 CSV round-trip / 식별 헬퍼
python -m tests.test_pipeline    # matcher→changeset→apply (네트워크/LLM 불필요)
```

## 구성
```
analyzer-tba/
├── config.yaml          # 경로/임계값/모델 설정
├── src/
│   ├── ingest.py        # GitHub Issue + 댓글 수집
│   ├── extract.py       # 이슈 텍스트 → 구조화 레코드 (Gemini + 검증)
│   ├── csv_store.py     # 정본 CSV 로드/저장(round-trip)
│   ├── matcher.py       # NEW/UPDATE/UNCHANGED 분류
│   ├── diff.py          # 필드 단위 변경 + 히스토리 패치
│   ├── changeset.py     # 제안 직렬화(JSON)
│   ├── apply.py         # accept분만 반영
│   ├── report.py        # PR 본문 Markdown
│   └── run.py           # CLI 엔트리포인트
├── proposals/           # 생성된 제안(휘발성, gitignore)
└── tests/
```
