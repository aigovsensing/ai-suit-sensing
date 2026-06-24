# ⚙️ GitHub Actions 자동화 가이드

> **대상**: 이 프로젝트의 GitHub Actions 워크플로우 설정 및 자동화 방법을 학습합니다.  
> **관련 파일**: [`.github/workflows/lawsuit-monitor.yml`](../.github/workflows/lawsuit-monitor.yml)

---

## 1. GitHub Actions란?

GitHub Actions는 GitHub 저장소에서 **CI/CD(지속적 통합/배포)** 및 **자동화 작업**을 실행할 수 있는 플랫폼입니다.

- **비용**: Public 저장소는 무료 / Private 저장소는 월 2,000분 무료
- **실행 환경**: ubuntu-latest, windows-latest, macos-latest
- **트리거**: Push, PR, Schedule(cron), 수동(workflow_dispatch) 등

---

## 2. 워크플로우 파일 구조

워크플로우 파일은 `.github/workflows/` 폴더에 YAML 형식으로 저장합니다.

```yaml
name: 워크플로우 이름

on:              # 트리거 조건
  schedule:
    - cron: "0 0 * * *"    # 매일 UTC 00:00
  workflow_dispatch: {}     # 수동 실행 허용

permissions:     # GitHub API 권한
  contents: write
  issues: write

jobs:
  job-name:
    runs-on: ubuntu-latest   # 실행 환경
    steps:
      - name: 단계 이름
        uses: actions/checkout@v4   # 액션 사용
      
      - name: Python 실행
        run: python my_script.py   # 직접 명령 실행
        env:
          MY_SECRET: ${{ secrets.MY_SECRET }}
```

---

## 3. 이 프로젝트의 워크플로우

### 실행 스케줄 ([lawsuit-monitor.yml](../.github/workflows/lawsuit-monitor.yml))

```yaml
on:
  schedule:
    # 업무시간 (KST 08:00-17:00 = UTC 23:00-08:00): 매 1시간
    - cron: "0 23,0-8 * * *"

    # 비업무시간 (KST 18:00-06:00 = UTC 09:00-21:00): 매 3시간
    - cron: "0 9-21/3 * * *"

  workflow_dispatch: {}   # 수동 실행
```

### KST ↔ UTC 변환표

| KST | UTC | 실행 여부 |
|-----|-----|---------|
| 08:00 | 23:00 (전날) | ✅ 매시간 |
| 09:00 | 00:00 | ✅ 매시간 |
| 17:00 | 08:00 | ✅ 매시간 |
| 18:00 | 09:00 | ✅ 3시간 |
| 21:00 | 12:00 | ✅ 3시간 |

---

## 4. Cron 표현식

```
┌──── 분 (0-59)
│  ┌─── 시 (0-23)
│  │  ┌── 일 (1-31)
│  │  │  ┌─ 월 (1-12)
│  │  │  │  ┌ 요일 (0-6, 0=일요일)
│  │  │  │  │
*  *  *  *  *
```

### 주요 예시

| cron 표현식 | 실행 시점 |
|------------|---------|
| `0 * * * *` | 매시간 정각 |
| `0 9 * * *` | 매일 UTC 09:00 |
| `0 0 * * 1` | 매주 월요일 UTC 00:00 |
| `*/5 * * * *` | 매 5분 (최소 간격) |
| `0 0,6,12,18 * * *` | 매일 4회 (6시간 간격) |
| `0 9-17 * * 1-5` | 평일 09:00~17:00 매시간 |
| `0 23,0-8 * * *` | UTC 23:00 + 00:00~08:00 |

> 🛠️ **도구**: [crontab.guru](https://crontab.guru/) 에서 cron 표현식 시각적으로 확인

---

## 5. Secrets & Variables 설정

### GitHub Secrets (민감 정보)

1. 저장소 → **Settings** → **Secrets and variables** → **Actions**
2. **"New repository secret"** 클릭
3. Name과 Value 입력

이 프로젝트에서 사용하는 Secrets:

| Secret 이름 | 용도 |
|------------|------|
| `SLACK_WEBHOOK_URL` | Slack 알림 웹훅 URL |
| `COURTLISTENER_TOKEN` | CourtListener API 토큰 |
| `GEMINI_API_KEY` | Google Gemini API 키 |
| `SMTP_PASS` | Gmail SMTP 앱 비밀번호 |

### GitHub Variables (비민감 설정)

1. 저장소 → **Settings** → **Secrets and variables** → **Actions** → **Variables** 탭
2. **"New repository variable"** 클릭

이 프로젝트에서 사용하는 Variables:

| Variable 이름 | 기본값 | 용도 |
|--------------|--------|------|
| `LOOKBACK_DAYS` | `3` | 뉴스/소송 수집 기간 (일) |
| `GEMINI_AISUIT_TREND_DAYS` | - | 조간뉴스 분석 활성화 |
| `PREVIOUS_ITEM_DEDUP_DAYS` | - | 이전 이슈 중복 제거 범위 |
| `ENABLE_EMAIL_SENDER` | `0` | 이메일 발송 활성화 (`1`=ON) |
| `DEBUG` | `0` | 디버그 모드 (`1`=ON) |
| `SHOW_DOCKET_CANDIDATES` | - | 도켓 후보 Top3 표기 |
| `COLLAPSE_LONG_CELLS` | - | 긴 셀 접기 |
| `COLLAPSE_ARTICLE_URLS` | - | 기사 URL 접기 |

### 워크플로우에서 Secrets/Variables 사용

```yaml
env:
  # Secret 사용
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}

  # Variable 사용 (없으면 기본값 '0')
  ENABLE_EMAIL_SENDER: ${{ vars.ENABLE_EMAIL_SENDER || '0' }}

  # Secret과 Variable 중 존재하는 것 사용
  GEMINI_AISUIT_TREND_DAYS: ${{ vars.GEMINI_AISUIT_TREND_DAYS || secrets.GEMINI_AISUIT_TREND_DAYS }}
```

---

## 6. 워크플로우 수동 실행

1. 저장소 → **Actions** 탭
2. 왼쪽에서 워크플로우 이름 선택 (`lawsuit-monitor`)
3. 우측 **"Run workflow"** 드롭다운 클릭
4. 브랜치 선택 → **"Run workflow"** 클릭

> ✅ 디버깅/테스트 시 반드시 `workflow_dispatch: {}` 를 트리거에 포함시켜야 수동 실행 가능

---

## 7. GitHub Permissions 설정

이 프로젝트는 GitHub API를 통해 Issue를 생성/수정합니다:

```yaml
permissions:
  contents: write    # 코드 커밋/푸시 권한 (이미지 커밋용)
  issues: write      # Issue 생성/수정/종료 권한
```

### GitHub Token 사용

```yaml
env:
  GITHUB_TOKEN: ${{ github.token }}     # 자동 제공 토큰
  GITHUB_OWNER: ${{ github.repository_owner }}
  GITHUB_REPO: ${{ github.event.repository.name }}
```

---

## 8. 워크플로우 실행 로그 확인

1. 저장소 → **Actions** 탭
2. 실행 기록에서 특정 실행 클릭
3. Job 이름 클릭 → 단계별 로그 확인
4. 실패 시 ❌ 표시 → 해당 단계 로그에서 오류 확인

### 주요 디버깅 방법

```yaml
# 환경 변수 출력 (디버깅용)
- name: Debug environment
  run: |
    echo "LOOKBACK_DAYS=$LOOKBACK_DAYS"
    echo "DEBUG=$DEBUG"
  env:
    LOOKBACK_DAYS: ${{ vars.LOOKBACK_DAYS }}
    DEBUG: ${{ vars.DEBUG }}
```

---

## 9. 참고 자료

| 링크 | 설명 |
|------|------|
| [GitHub Actions 공식 문서](https://docs.github.com/en/actions) | 전체 문서 |
| [crontab.guru](https://crontab.guru/) | Cron 표현식 생성/검증 |
| [actions/checkout](https://github.com/actions/checkout) | 코드 체크아웃 액션 |
| [actions/setup-python](https://github.com/actions/setup-python) | Python 환경 설정 액션 |
