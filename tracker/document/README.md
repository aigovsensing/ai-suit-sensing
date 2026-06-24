# 📚 Document — 학습 및 참고 문서 인덱스

이 폴더는 **ai-suit-tracker** 프로젝트에서 활용하는 외부 서비스·라이브러리·알고리즘에 대한 학습 문서 모음입니다.  
웹 브라우저와 Python 코드 예시를 중심으로 실전적인 사용법을 정리했습니다.

---

## 📂 문서 목록

| 파일 | 주제 | 핵심 내용 |
|------|------|----------|
| [google-rss.md](./google-rss.md) | 📰 Google News RSS | 뉴스 피드 수집, URL 파라미터, feedparser 사용법 |
| [courtlistener.md](./courtlistener.md) | ⚖️ CourtListener API | 소송 문서 검색, REST API v4, 도켓 조회 |
| [recap.md](./recap.md) | 🗂️ RECAP & PACER | PACER 계정 생성, RECAP 브라우저 확장, PDF 문서 접근 |
| [deduplication.md](./deduplication.md) | 🔁 유사도 & 중복 제거 | Exact Match, BM25, 코사인 유사도, Gemini 임베딩 |
| [gemini-api.md](./gemini-api.md) | 🤖 Gemini API | 텍스트 요약, 임베딩 생성, 프롬프트 설계 |
| [github-actions.md](./github-actions.md) | ⚙️ GitHub Actions | 스케줄 자동화, Secrets/Variables, cron 설정 |
| [github-issues.md](./github-issues.md) | 🔗 GitHub Issues API | Issue 자동 생성, 댓글 누적, 라벨 관리 |
| [slack-webhook.md](./slack-webhook.md) | 📨 Slack Webhook | 채널 알림 전송, mrkdwn 서식, Block Kit |
| [email-smtp.md](./email-smtp.md) | 📧 Gmail SMTP | HTML 이메일 발송, 앱 비밀번호, Markdown→HTML |

---

## 🔗 프로젝트 데이터 흐름

```
[뉴스 수집]                [소송 수집]
Google News RSS       CourtListener API / PACER
     │                         │
     ▼                         ▼
 feedparser               RECAP Documents
     │                         │
     └──────────┬──────────────┘
                ▼
         [중복 제거 (dedup.py)]
         Exact Match → BM25 → 시맨틱 임베딩
                ▼
         [AI 분석 (Gemini API)]
         조간뉴스 (동향 요약) / 석간뉴스 (당일 요약)
                ▼
         [리포트 발행]
    GitHub Issues ── Slack ── Email (HTML)
```

---

## 🌐 주요 웹 서비스 링크

| 서비스 | URL | 용도 |
|--------|-----|------|
| Google News | https://news.google.com | 뉴스 RSS 피드 수집 |
| CourtListener | https://www.courtlistener.com | 소송 검색 및 API |
| PACER | https://pacer.uscourts.gov | 연방법원 문서 (유료) |
| RECAP 아카이브 | https://www.courtlistener.com/recap/ | PACER 문서 무료 검색 |
| Google AI Studio | https://aistudio.google.com | Gemini API 키 발급/테스트 |
| GitHub Actions | https://github.com/features/actions | 자동화 워크플로우 |
| Slack API | https://api.slack.com | Webhook 생성 |
| crontab.guru | https://crontab.guru | Cron 표현식 생성기 |

---

## ⚙️ 환경변수 전체 목록

| 환경변수 | 위치 | 설명 |
|---------|------|------|
| `GITHUB_TOKEN` | Secret (자동) | GitHub API 인증 토큰 |
| `GITHUB_OWNER` | 자동 | 저장소 소유자 |
| `GITHUB_REPO` | 자동 | 저장소 이름 |
| `SLACK_WEBHOOK_URL` | Secret | Slack 알림 웹훅 URL |
| `COURTLISTENER_TOKEN` | Secret | CourtListener API 토큰 |
| `GEMINI_API_KEY` | Secret | Gemini AI API 키 |
| `SMTP_PASS` | Secret | Gmail 앱 비밀번호 |
| `ENABLE_EMAIL_SENDER` | Variable | 이메일 발송 ON/OFF (`1`=ON) |
| `LOOKBACK_DAYS` | Variable | 뉴스/소송 수집 기간 (기본: `3`) |
| `GEMINI_AISUIT_TREND_DAYS` | Variable | 조간뉴스 분석 활성화 |
| `PREVIOUS_ITEM_DEDUP_DAYS` | Variable | 이전 이슈 중복 제거 범위 |
| `BM25_SEMANTIC_DEDUP` | Variable | BM25 중복 제거 (`1`=ON) |
| `BM25_DEDUP_THRESHOLD` | Variable | BM25 임계값 (기본: `3.0`) |
| `GEMINI_SEMANTIC_DEDUP` | Variable | 시맨틱 중복 제거 (`1`=ON) |
| `SEMANTIC_DEDUP_THRESHOLD` | Variable | 코사인 유사도 임계값 (기본: `0.85`) |
| `DEBUG` | Variable | 디버그 모드 (`1`=ON) |
