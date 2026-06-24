import os
import json
import smtplib
import markdown as md_lib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .utils import debug_log

# ─────────────────────────────────────────────
# HTML 이메일 템플릿 (인라인 CSS 스타일 포함)
# Gmail 등 주요 이메일 클라이언트 호환
# ─────────────────────────────────────────────
_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{subject}</title>
</head>
<body style="margin:0;padding:0;background:#f4f6f9;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f9;padding:24px 0;">
  <tr>
    <td align="center">
      <table width="700" cellpadding="0" cellspacing="0"
             style="max-width:700px;background:#ffffff;border-radius:10px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.08);overflow:hidden;">

        <!-- 헤더 -->
        <tr>
          <td style="background:linear-gradient(135deg,#1a237e 0%,#283593 60%,#1565c0 100%);
                     padding:24px 32px;">
            <p style="margin:0;font-size:12px;color:#90caf9;letter-spacing:1px;text-transform:uppercase;">
              AI Gov Sensing
            </p>
            <h1 style="margin:6px 0 0;font-size:20px;font-weight:700;color:#ffffff;line-height:1.4;">
              {title_line}
            </h1>
          </td>
        </tr>

        <!-- 본문 -->
        <tr>
          <td style="padding:32px 32px 24px;">
            <div style="color:#212121;font-size:14px;line-height:1.8;">
              {body_html}
            </div>
          </td>
        </tr>

        <!-- 푸터 -->
        <tr>
          <td style="background:#f8f9fa;padding:16px 32px;border-top:1px solid #e0e0e0;">
            <p style="margin:0;font-size:11px;color:#9e9e9e;text-align:center;">
              이 메일은 <strong>ai-suit-tracker</strong> 자동화 시스템에서 발송되었습니다.
              &nbsp;|&nbsp; Powered by Gemini &amp; GitHub Actions
            </p>
          </td>
        </tr>

      </table>
    </td>
  </tr>
</table>
</body>
</html>
"""

# Markdown → HTML 변환 시 적용할 확장 기능
_MD_EXTENSIONS = [
    "tables",          # | 테이블 지원
    "fenced_code",     # ``` 코드블록 지원
    "nl2br",           # 줄바꿈 → <br>
    "sane_lists",      # 리스트 들여쓰기 개선
]

# 변환된 HTML 요소에 이메일 클라이언트 호환 인라인 스타일 적용
_INLINE_STYLES = [
    # 제목
    ("h1", "font-size:22px;font-weight:700;color:#1a237e;border-bottom:2px solid #e3f2fd;"
           "padding-bottom:8px;margin:24px 0 12px;"),
    ("h2", "font-size:18px;font-weight:700;color:#1565c0;border-bottom:1px solid #e3f2fd;"
           "padding-bottom:6px;margin:20px 0 10px;"),
    ("h3", "font-size:15px;font-weight:700;color:#283593;margin:16px 0 8px;"),
    ("h4", "font-size:14px;font-weight:700;color:#37474f;margin:12px 0 6px;"),
    # 텍스트
    ("p",  "margin:0 0 12px;color:#212121;font-size:14px;line-height:1.8;"),
    # 링크
    ("a",  "color:#1565c0;text-decoration:none;"),
    # 코드
    ("code", "background:#f5f5f5;border:1px solid #e0e0e0;border-radius:3px;"
             "padding:1px 5px;font-family:monospace;font-size:13px;color:#c62828;"),
    ("pre",  "background:#f5f5f5;border:1px solid #e0e0e0;border-radius:6px;"
             "padding:14px 16px;overflow-x:auto;margin:12px 0;"),
    # 테이블
    ("table", "width:100%;border-collapse:collapse;margin:16px 0;font-size:13px;"),
    ("th",    "background:#e8eaf6;color:#1a237e;font-weight:700;padding:9px 12px;"
              "border:1px solid #c5cae9;text-align:left;"),
    ("td",    "padding:8px 12px;border:1px solid #e0e0e0;color:#212121;vertical-align:top;"),
    # 리스트
    ("ul", "margin:8px 0 12px 0;padding-left:22px;"),
    ("ol", "margin:8px 0 12px 0;padding-left:22px;"),
    ("li", "margin:4px 0;color:#212121;font-size:14px;line-height:1.7;"),
    # 강조
    ("strong", "font-weight:700;color:#212121;"),
    ("em",     "font-style:italic;color:#424242;"),
    # 인용
    ("blockquote", "margin:12px 0;padding:10px 16px;border-left:4px solid #1565c0;"
                   "background:#e8eaf6;border-radius:0 4px 4px 0;color:#37474f;"),
    # 수평선
    ("hr", "border:none;border-top:1px solid #e0e0e0;margin:20px 0;"),
]


def _apply_inline_styles(html: str) -> str:
    """BeautifulSoup을 사용하여 HTML 태그에 인라인 스타일을 적용합니다."""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        style_map = dict(_INLINE_STYLES)

        for tag_name, style in style_map.items():
            for tag in soup.find_all(tag_name):
                existing = tag.get("style", "")
                tag["style"] = (existing + ";" + style).lstrip(";")

        # 짝수/홀수 행 배경색 (테이블 가독성)
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            for i, row in enumerate(rows[1:], 1):  # 헤더 제외
                bg = "#fafafa" if i % 2 == 0 else "#ffffff"
                row["style"] = f"background:{bg};"

        return str(soup)
    except Exception:
        return html


def _markdown_to_html(text: str) -> str:
    """Markdown 텍스트를 인라인 스타일이 적용된 HTML로 변환합니다."""
    try:
        # GitHub-style alert (> [!NOTE] 등) → 색상 박스로 변환
        import re
        alert_map = {
            "NOTE":      ("#e3f2fd", "#1565c0", "#1976d2", "ℹ️"),
            "TIP":       ("#e8f5e9", "#2e7d32", "#388e3c", "💡"),
            "IMPORTANT": ("#ede7f6", "#4527a0", "#512da8", "⚡"),
            "WARNING":   ("#fff8e1", "#f57f17", "#f9a825", "⚠️"),
            "CAUTION":   ("#ffebee", "#b71c1c", "#c62828", "🚨"),
        }

        def replace_alert(m):
            kind = m.group(1).upper()
            body_raw = m.group(2).strip()
            # 인용 마커(> ) 제거
            body_clean = re.sub(r"^>\s?", "", body_raw, flags=re.MULTILINE).strip()
            cfg = alert_map.get(kind, ("#f5f5f5", "#424242", "#616161", "📌"))
            bg, border, title_color, icon = cfg
            return (
                f'<div style="background:{bg};border-left:4px solid {border};'
                f'border-radius:0 6px 6px 0;padding:12px 16px;margin:12px 0;">'
                f'<p style="margin:0 0 6px;font-weight:700;color:{title_color};font-size:13px;">'
                f'{icon} {kind}</p>'
                f'<div style="color:#212121;font-size:13px;line-height:1.7;">{body_clean}</div>'
                f'</div>'
            )

        # alert 블록 패턴 매칭 (> [!KIND]\n> body 형식)
        text = re.sub(
            r"> \[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\n((?:>.*\n?)+)",
            replace_alert,
            text,
            flags=re.IGNORECASE,
        )

        raw_html = md_lib.markdown(text, extensions=_MD_EXTENSIONS)
        return _apply_inline_styles(raw_html)
    except Exception as e:
        debug_log(f"Markdown → HTML 변환 실패 (plain text 폴백): {e}")
        # 실패 시 plain text를 간단히 <p>로 감싸서 반환
        import html as html_mod
        escaped = html_mod.escape(text)
        return f"<pre style='white-space:pre-wrap;font-family:inherit;'>{escaped}</pre>"


def _extract_title_line(subject: str, content: str) -> str:
    """이메일 헤더에 표시할 제목 라인을 추출합니다."""
    for line in content.splitlines():
        stripped = line.strip().lstrip("#").strip()
        if stripped and ("조간뉴스" in stripped or "석간뉴스" in stripped):
            return stripped
    # 없으면 이메일 제목에서 따옴표 내 텍스트 추출
    import re
    m = re.search(r'"(.+?)"', subject)
    return m.group(1) if m else subject


def get_subject_for_report(report_body: str, fallback_type: str, lookback_days: int = 3) -> str:
    """
    보고서 본문에서 제목(조간뉴스/석간뉴스)을 파싱하여 이메일 제목을 생성합니다.
    """
    for line in report_body.splitlines():
        line = line.strip()
        if "(조간뉴스)" in line:
            idx = line.find("(조간뉴스)")
            title_part = line[idx:].strip()
            title_part = title_part.replace("**", "").replace("*", "")
            return f'[ai.gov.sensing] "{title_part}"'
        elif "(석간뉴스)" in line:
            idx = line.find("(석간뉴스)")
            title_part = line[idx:].strip()
            title_part = title_part.replace("**", "").replace("*", "")
            return f'[ai.gov.sensing] "{title_part}"'

    if fallback_type == "morning":
        return f'[ai.gov.sensing] "(조간뉴스) {lookback_days}일간의 소송센싱 주요 동향 현황"'
    else:
        return '[ai.gov.sensing] "(석간뉴스) 당일 신규/업데이트 소송건 요약 보고서 (Gemini)"'


def send_email_report(subject: str, content: str) -> None:
    """
    Gmail SMTP를 사용하여 email.json에 등록된 설정 및 수신자들로 이메일을 발송합니다.
    - Markdown → HTML 변환 후 multipart/alternative 형식으로 발송
    - plain text 폴백 포함 (HTML 미지원 클라이언트 대응)
    - [FIX] 수신자 전체를 단일 sendmail()로 발송하여 중복 수신 방지
    """
    enable_sender = os.environ.get("ENABLE_EMAIL_SENDER") == "1"
    if not enable_sender:
        debug_log("이메일 전송 기능이 비활성화 상태입니다. (ENABLE_EMAIL_SENDER != 1)")
        return

    # 설정 파일(email.json) 정보 읽기
    email_json_path = os.path.join("data", "email.json")
    config = {}
    if os.path.exists(email_json_path):
        try:
            with open(email_json_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(f"[ERROR] 이메일 설정 파일(email.json) 파싱 실패: {e}")
            return
    else:
        print(f"[ERROR] 이메일 설정 파일이 존재하지 않습니다: {email_json_path}")
        return

    # 설정 파일 값 추출 (기본값 설정)
    smtp_host = config.get("smtp_host", "smtp.gmail.com")
    smtp_port = config.get("smtp_port", 587)
    sender = config.get("sender", "")
    receivers = config.get("receivers", [])

    if not sender:
        print("[ERROR] email.json 내에 발신자 주소(sender)가 설정되지 않았습니다.")
        return

    if not receivers:
        print("[WARNING] email.json 내에 수신자(receivers) 목록이 비어 있습니다.")
        return

    # SMTP 앱 비밀번호 획득 (환경 변수 - GitHub Secrets)
    smtp_password = os.environ.get("SMTP_PASS") or os.environ.get("SMTP_PASSWORD")
    if not smtp_password:
        print("[ERROR] SMTP 비밀번호(SMTP_PASS 환경변수)가 설정되지 않았습니다.")
        return

    clean_receivers = [r.strip() for r in receivers if r.strip()]
    debug_log(f"이메일 발송 작업을 시작합니다. (수신인: {clean_receivers})")

    # ── HTML 변환 ──────────────────────────────────────────────
    title_line = _extract_title_line(subject, content)
    body_html  = _markdown_to_html(content)
    full_html  = _HTML_TEMPLATE.format(
        subject    = subject,
        title_line = title_line,
        body_html  = body_html,
    )

    # ── 이메일 메시지 구성 (multipart/alternative) ─────────────
    # alternative: 클라이언트가 HTML을 지원하면 HTML, 아니면 plain text를 표시
    msg = MIMEMultipart("alternative")
    msg["From"]    = sender
    msg["To"]      = ", ".join(clean_receivers)
    msg["Subject"] = subject

    # 1) plain text 파트 (폴백)
    msg.attach(MIMEText(content, "plain", "utf-8"))
    # 2) HTML 파트 (우선 표시)
    msg.attach(MIMEText(full_html, "html", "utf-8"))

    # ── SMTP 발송 (단일 sendmail로 중복 방지) ──────────────────
    try:
        debug_log(f"SMTP 서버 연결 중: {smtp_host}:{smtp_port}")
        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            server.starttls()
            server.login(sender, smtp_password)
            debug_log(f"이메일 일괄 전송 요청 중: {clean_receivers} (제목: {subject})")
            server.sendmail(sender, clean_receivers, msg.as_string())
            debug_log(f"이메일 전송 성공: {clean_receivers}")
    except Exception as e:
        print(f"[ERROR] 이메일 전송 중 SMTP 서버 오류 발생: {e}")
