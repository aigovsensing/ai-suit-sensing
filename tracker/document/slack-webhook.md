# 📨 Slack Webhook 사용 가이드

> **대상**: Slack Incoming Webhook을 활용하여 모니터링 알림을 Slack 채널로 전송하는 방법을 학습합니다.  
> **관련 파일**: [`src/slack.py`](../src/slack.py)

---

## 1. Slack Webhook이란?

**Incoming Webhook**은 외부 애플리케이션에서 Slack 채널로 메시지를 전송할 수 있는 URL입니다.

- 별도 봇 계정 없이 특정 채널에 메시지 전송 가능
- POST 요청으로 JSON 페이로드 전송
- Markdown 유사 서식(mrkdwn) 지원

---

## 2. Webhook URL 생성 방법

### Slack App 생성
1. [https://api.slack.com/apps](https://api.slack.com/apps) 접속
2. **"Create New App"** → **"From scratch"** 클릭
3. App 이름 입력, 워크스페이스 선택

### Incoming Webhook 활성화
1. 앱 설정 → **"Incoming Webhooks"** 클릭
2. **"Activate Incoming Webhooks"** 토글 ON
3. 하단 **"Add New Webhook to Workspace"** 클릭
4. 메시지를 보낼 채널 선택 → **"Allow"**
5. Webhook URL 복사:
   > 형식: `https://hooks.slack.com/services/{팀ID}/{채널ID}/{고유토큰}`  
   > 예: `hooks.slack.com/services/T.../B.../...` 형태로 생성됩니다.

### GitHub Secrets에 등록
```
Secret 이름: SLACK_WEBHOOK_URL
Secret 값:   https://hooks.slack.com/services/...
```

---

## 3. 메시지 전송 방법

### Python으로 기본 메시지 전송

```python
import requests
import json

webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

payload = {
    "text": "안녕하세요! AI 소송 모니터링 알림입니다. 🤖"
}

response = requests.post(
    webhook_url,
    data=json.dumps(payload),
    headers={"Content-Type": "application/json"},
    timeout=10,
)
print(f"상태: {response.status_code}")  # 200 = 성공
```

### 이 프로젝트의 구현 ([`src/slack.py`](../src/slack.py))

```python
import requests
import json

def post_to_slack(webhook_url: str, message: str) -> None:
    """Slack Webhook으로 메시지를 전송합니다."""
    payload = {"text": message}
    response = requests.post(
        webhook_url,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    response.raise_for_status()
```

---

## 4. Slack mrkdwn 서식

Slack은 GitHub Markdown과 다른 **mrkdwn** 서식을 사용합니다.

| 기능 | GitHub MD | Slack mrkdwn |
|------|-----------|-------------|
| 굵게 | `**텍스트**` | `*텍스트*` |
| 이탤릭 | `*텍스트*` | `_텍스트_` |
| 취소선 | `~~텍스트~~` | `~텍스트~` |
| 코드 | `` `코드` `` | `` `코드` `` |
| 코드 블록 | ` ```코드``` ` | ` ```코드``` ` |
| 링크 | `[텍스트](URL)` | `<URL\|텍스트>` |
| 이모지 | 📊 | `:bar_chart:` |

### Slack 이모지 코드 (자주 사용)

| 이모지 | 코드 |
|--------|------|
| 📊 | `:bar_chart:` |
| 🔗 | `:link:` |
| 🆕 | `:new:` |
| 🔴 | `:red_circle:` |
| ✅ | `:white_check_mark:` |
| ⚠️ | `:warning:` |
| 🔄 | `:arrows_counterclockwise:` |
| 📈 | `:chart_with_upwards_trend:` |

---

## 5. 이 프로젝트의 Slack 메시지 구조

```python
# src/run.py에서 Slack 메시지 구성
slack_lines = []
slack_lines.append(":bar_chart: AI 소송 모니터링")
slack_lines.append(f"🕒 {timestamp}")
slack_lines.append("")

# 중복 제거 요약
slack_lines.append(":arrows_counterclockwise: Dedup Summary")
slack_lines.append(f"└ News {slack_dedup_news}")
slack_lines.append(f"└ Cases {slack_dedup_cases}")
slack_lines.append("")

# 수집 현황
slack_lines.append(":chart_with_upwards_trend: Collection Status")
slack_lines.append(f"└ News: {len(lawsuits)}")
slack_lines.append(f"└ Cases: {docket_case_count} (Docs: {recap_doc_count})")
slack_lines.append("")

# GitHub Issue 링크
slack_lines.append(f":link: GitHub: <{issue_url}|#{issue_no}>")

# 최신 RECAP 문서 Top 3
slack_lines.append(":new: 최신 RECAP 문서 (820 Copyright)")
for c in top_cases:
    slack_lines.append(f"• {date} | <{docket_url}|{name}>")

message = "\n".join(slack_lines)
```

**실제 Slack 출력 예시:**
```
📊 AI 소송 모니터링
🕒 2026-06-24 08:00 KST

🔄 Dedup Summary
└ News 5건 총 15건 중 *5 (New)* 🔴
└ Cases 2건 총 8건 중 *2 (New)* 🔴

📈 Collection Status
└ News: 15
└ Cases: 8 (Docs: 6)

🔗 GitHub: #42

🆕 최신 RECAP 문서 (820 Copyright)
• 2026-06-23 | S.A. Jamendo v. NVIDIA Corp
• 2026-06-22 | Authors Guild v. OpenAI
• 2026-06-21 | Getty Images v. Stability AI
```

---

## 6. Block Kit (고급 메시지 서식)

더 풍부한 UI를 원한다면 Slack Block Kit을 활용하세요.

```python
payload = {
    "blocks": [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📊 AI 소송 모니터링 리포트",
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*뉴스 수집*\n{news_count}건"},
                {"type": "mrkdwn", "text": f"*소송 감지*\n{case_count}건"},
            ]
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "GitHub Issue 보기"},
                    "url": issue_url,
                    "style": "primary",
                }
            ]
        }
    ]
}
```

**Block Kit 빌더**: https://app.slack.com/block-kit-builder

---

## 7. 웹훅 테스트 (브라우저 없이)

```bash
# curl로 테스트
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"테스트 메시지입니다!"}' \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

## 8. 참고 자료

| 링크 | 설명 |
|------|------|
| [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks) | 공식 문서 |
| [Slack API](https://api.slack.com) | 앱 생성 및 관리 |
| [Block Kit Builder](https://app.slack.com/block-kit-builder) | 메시지 UI 빌더 |
| [mrkdwn 서식](https://api.slack.com/reference/surfaces/formatting) | Slack 서식 문서 |
