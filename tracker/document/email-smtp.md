# 📧 Gmail SMTP 이메일 발송 가이드

> **대상**: Gmail SMTP를 사용하여 Python에서 HTML 포맷 이메일을 자동 발송하는 방법을 학습합니다.  
> **관련 파일**: [`src/email_sender.py`](../src/email_sender.py), [`data/email.json`](../data/email.json)

---

## 1. Gmail SMTP란?

Gmail의 SMTP(Simple Mail Transfer Protocol) 서버를 통해 외부 프로그램에서 Gmail 계정으로 이메일을 발송할 수 있습니다.

| 항목 | 값 |
|------|---|
| **SMTP 서버** | `smtp.gmail.com` |
| **포트 (TLS)** | `587` |
| **포트 (SSL)** | `465` |
| **암호화** | STARTTLS (포트 587) |

---

## 2. Gmail 앱 비밀번호 발급 (필수)

구글 계정의 2단계 인증이 활성화된 경우, 일반 비밀번호 대신 **앱 비밀번호(App Password)**를 발급해야 합니다.

### 발급 절차
1. Google 계정 → **[보안](https://myaccount.google.com/security)** 탭
2. "Google에 로그인" 섹션 → **2단계 인증** 확인 (반드시 활성화되어 있어야 함)
3. **[앱 비밀번호](https://myaccount.google.com/apppasswords)** 클릭
4. 앱 선택: **"기타(맞춤 이름)"** → 이름 입력 (예: `ai-suit-tracker`)
5. **"생성"** 클릭 → 16자리 비밀번호 발급
6. GitHub Secrets에 등록:
   ```
   Secret 이름: SMTP_PASS
   Secret 값:   xxxx xxxx xxxx xxxx   (공백 포함 그대로 사용 가능)
   ```

> ⚠️ **주의**: 앱 비밀번호는 발급 시에만 확인 가능합니다. 반드시 안전한 곳에 저장하세요.

---

## 3. email.json 설정 ([`data/email.json`](../data/email.json))

```json
{
  "_comment": "수신자(receivers) 목록에 발신자와 동일한 주소가 있으면 자신에게도 전송됩니다.",
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "sender": "your-email@gmail.com",
  "receivers": [
    "recipient1@gmail.com",
    "recipient2@company.com"
  ]
}
```

---

## 4. Python으로 이메일 발송

### 기본 HTML 이메일 발송

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_html_email(
    smtp_host: str,
    smtp_port: int,
    sender: str,
    password: str,
    receivers: list,
    subject: str,
    html_body: str,
    plain_body: str = "",
):
    # multipart/alternative: HTML 우선, plain text 폴백
    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["To"] = ", ".join(receivers)
    msg["Subject"] = subject

    # 1) Plain text 파트 (HTML 미지원 클라이언트용)
    if plain_body:
        msg.attach(MIMEText(plain_body, "plain", "utf-8"))

    # 2) HTML 파트 (우선 표시)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    # SMTP 연결 및 발송 (단일 sendmail로 중복 방지)
    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
        server.starttls()           # TLS 암호화 시작
        server.login(sender, password)
        server.sendmail(sender, receivers, msg.as_string())

    print(f"이메일 전송 완료: {receivers}")
```

### Markdown → HTML 변환 (이 프로젝트)

```python
import markdown

def markdown_to_html(text: str) -> str:
    """Markdown 텍스트를 HTML로 변환합니다."""
    html = markdown.markdown(
        text,
        extensions=[
            "tables",       # | 표 | 형식 지원
            "fenced_code",  # ```코드블록``` 지원
            "nl2br",        # 줄바꿈 → <br>
            "sane_lists",   # 리스트 들여쓰기 개선
        ]
    )
    return html
```

---

## 5. 이 프로젝트의 이메일 발송 흐름

```
[GitHub Actions 실행]
        ↓
[석간뉴스 생성] (github_issue.py)
  └─ generate_daily_report_from_data()  → Markdown 보고서
  └─ send_email_report(subject, content)
        ↓
[email_sender.py]
  └─ email.json 읽기 (sender, receivers)
  └─ SMTP_PASS 환경변수 읽기
  └─ Markdown → HTML 변환
  └─ HTML 이메일 템플릿 적용
  └─ multipart/alternative 메시지 구성
  └─ smtplib.SMTP.sendmail() → 전체 수신자에게 1회 발송
        ↓
[수신자 받은편지함]
  └─ HTML 렌더링된 보기 좋은 이메일 표시
```

---

## 6. 이메일 HTML 템플릿 구조

이 프로젝트의 이메일은 **인라인 CSS**로 스타일을 적용합니다 (대부분의 이메일 클라이언트는 외부 CSS를 차단).

```html
<!DOCTYPE html>
<html lang="ko">
<body style="background:#f4f6f9;font-family:'Segoe UI',Arial,sans-serif;">
  <!-- 외부 래퍼 테이블 -->
  <table width="100%" style="background:#f4f6f9;padding:24px 0;">
    <tr><td align="center">

      <!-- 콘텐츠 테이블 (최대 700px) -->
      <table width="700" style="background:#fff;border-radius:10px;">

        <!-- 헤더 (파란색 그라데이션) -->
        <tr>
          <td style="background:linear-gradient(135deg,#1a237e,#1565c0);padding:24px;">
            <h1 style="color:#fff;">보고서 제목</h1>
          </td>
        </tr>

        <!-- 본문 (변환된 Markdown HTML) -->
        <tr>
          <td style="padding:32px;">
            {body_html}
          </td>
        </tr>

        <!-- 푸터 -->
        <tr>
          <td style="background:#f8f9fa;padding:16px;border-top:1px solid #e0e0e0;">
            <p style="color:#9e9e9e;text-align:center;font-size:11px;">
              자동화 시스템 발송 | Powered by Gemini & GitHub Actions
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
```

---

## 7. 이메일 클라이언트별 호환성

| 클라이언트 | HTML 지원 | 외부 CSS | 인라인 CSS |
|-----------|---------|---------|---------|
| Gmail (웹) | ✅ | ❌ | ✅ |
| Outlook | ✅ | ❌ | ✅ (제한) |
| Apple Mail | ✅ | ✅ | ✅ |
| Thunderbird | ✅ | ✅ | ✅ |
| 모바일 Gmail | ✅ | ❌ | ✅ |

> 💡 **인라인 CSS를 사용하는 이유**: 대부분의 이메일 클라이언트가 보안 이유로 `<style>` 태그나 외부 CSS 파일을 차단하기 때문입니다.

---

## 8. 이메일 발송 테스트

### 로컬 테스트 스크립트
```python
# scratch/test_email.py
import os
os.environ["ENABLE_EMAIL_SENDER"] = "1"
os.environ["SMTP_PASS"] = "your-app-password"

from src.email_sender import send_email_report

sample_content = """
## 🧠 (석간뉴스) 테스트 보고서

### 1. 테스트 항목

| 항목 | 상태 |
|------|------|
| HTML 변환 | ✅ |
| 테이블 렌더링 | ✅ |
| 링크 | [CourtListener](https://www.courtlistener.com) |

> [!NOTE]
> 이것은 테스트 메시지입니다.
"""

send_email_report(
    subject='[ai.gov.sensing] "(석간뉴스) 테스트 보고서"',
    content=sample_content,
)
```

---

## 9. 자주 발생하는 오류

| 오류 | 원인 | 해결 방법 |
|------|------|---------|
| `SMTPAuthenticationError` | 앱 비밀번호 오류 | 앱 비밀번호 재발급 |
| `SMTPConnectError` | 네트워크/방화벽 | 포트 587 열림 확인 |
| `SSL: CERTIFICATE_VERIFY_FAILED` | 인증서 오류 | `ssl.create_default_context()` 사용 |
| 이메일 2번 수신 | 수신자별 sendmail 루프 | 단일 `sendmail(sender, all_receivers, msg)` 사용 |
| 스팸함으로 분류 | 회사 방화벽/필터 | SPF/DKIM 설정 또는 개인 이메일 사용 |

---

## 10. 참고 자료

| 링크 | 설명 |
|------|------|
| [Gmail 앱 비밀번호](https://myaccount.google.com/apppasswords) | 앱 비밀번호 발급 |
| [Python smtplib 문서](https://docs.python.org/3/library/smtplib.html) | 표준 라이브러리 |
| [Python email 문서](https://docs.python.org/3/library/email.html) | 이메일 메시지 구성 |
| [markdown 라이브러리](https://python-markdown.github.io/) | Markdown → HTML 변환 |
| [Can I Email](https://www.caniemail.com/) | 이메일 클라이언트별 CSS 지원 현황 |
