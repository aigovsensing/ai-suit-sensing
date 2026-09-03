import os
import json
import smtplib
from datetime import datetime
from zoneinfo import ZoneInfo
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
      <!-- 본문 폭: 고정 700px가 좁아 960px로 확대.
           width=100% + max-width 조합이라 좁은 화면(모바일)에서는 100%로 줄어든다. -->
      <table width="960" cellpadding="0" cellspacing="0"
             style="width:100%;max-width:960px;background:#ffffff;border-radius:10px;
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
              이 메일은 <strong><a href="https://github.com/aigovsensing/ai-suit-sensing/" style="color:#1a73e8;text-decoration:underline;">ai-suit-sensing</a></strong> 자동화 시스템에서 발송되었습니다.
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
        if stripped and ("조간뉴스" in stripped or "석간뉴스" in stripped or "당일 소송건들 통합 정리 자료" in stripped):
            return stripped
    # 없으면 이메일 제목에서 따옴표 내 텍스트 추출
    import re
    m = re.search(r'"(.+?)"', subject)
    return m.group(1) if m else subject


def get_subject_for_report(report_body: str, fallback_type: str, lookback_days: int = 3) -> str:
    """
    보고서 본문 제목에서 날짜·기간을 파싱하여 이메일 제목을 조립합니다.

    - 조간: [AI 학습데이터 소송] YYYY-MM-DD 조간 | 소송 동향 (최근 N일간)
      (N은 본문 제목의 "{N}일간의"에서 추출, 없으면 lookback_days 인자 사용
       — GEMINI_AISUIT_TREND_DAYS 환경변수로 결정되는 동적 값)
    - 석간: [AI 학습데이터 소송] YYYY-MM-DD 석간 | 소송 브리핑 (최근 1일간)
      (석간은 '당일 이슈'에 취합된 데이터만 요약하므로 기간이 항상 1일 고정)

    본문(GitHub 이슈 댓글) 제목은 "(조간뉴스: YYYY-MM-DD)" 형식을 유지하며,
    이메일 제목만 메일함 날짜순 열람에 맞춰 재구성한다.
    """
    import re

    for line in report_body.splitlines():
        line = line.strip()
        # "(조간뉴스)" / "(조간뉴스: 2026-07-02)" 모두 매칭되도록 닫는 괄호 없이 탐색
        if "(조간뉴스" in line or "(석간뉴스" in line:
            is_morning = "(조간뉴스" in line
            m_date = re.search(r"\d{4}-\d{2}-\d{2}", line)
            date_str = m_date.group(0) if m_date else datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")
            if is_morning:
                m_days = re.search(r"(\d+)일간의", line)
                days = int(m_days.group(1)) if m_days else lookback_days
                return f"[AI 학습데이터 소송] {date_str} 조간 | 소송 동향 (최근 {days}일간)"
            return f"[AI 학습데이터 소송] {date_str} 석간 | 소송 브리핑 (최근 1일간)"

    # 본문에서 제목을 찾지 못한 경우의 폴백 (KST 오늘 날짜 표기)
    today_kst = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")
    if fallback_type == "morning":
        return f"[AI 학습데이터 소송] {today_kst} 조간 | 소송 동향 (최근 {lookback_days}일간)"
    return f"[AI 학습데이터 소송] {today_kst} 석간 | 소송 브리핑 (최근 1일간)"


# 리포트 타입별 발송 여부를 제어하는 환경변수 이름
# (마스터 스위치 ENABLE_EMAIL_SENDER=1 이 켜져 있을 때만 의미가 있으며,
#  각 값은 기본 활성('1')이고 명시적으로 '0'일 때만 해당 타입을 비활성화한다)
_REPORT_TYPE_ENV = {
    "morning":      "ENABLE_EMAIL_MORNING",       # 🗓️ 조간뉴스
    "evening":      "ENABLE_EMAIL_EVENING",       # 🧠 석간뉴스
    "consolidated": "ENABLE_EMAIL_CONSOLIDATED",  # 📑 당일 소송건들 통합 정리 리포트
}


def _is_report_type_enabled(report_type: str | None) -> bool:
    """리포트 타입별 발송 스위치를 확인합니다. (미지정/미설정 시 기본 활성)"""
    if not report_type:
        return True
    env_key = _REPORT_TYPE_ENV.get(report_type)
    if not env_key:
        return True
    # 기본 '1'(활성). GitHub Actions에서 Variable 미설정 시 ""가 들어와도 활성으로 간주.
    # 명시적으로 '0'을 설정한 경우에만 비활성화한다.
    return os.environ.get(env_key, "1") != "0"


def _clean_list(values) -> list:
    """문자열 리스트에서 공백 제거 + 빈 값 제외."""
    if not isinstance(values, list):
        return []
    return [v.strip() for v in values if isinstance(v, str) and v.strip()]


def _resolve_receivers(config: dict, report_type: str | None) -> list:
    """
    리포트 종류(morning/evening/consolidated)별 수신자 목록을 결정합니다. (합집합 방식)

    - 공통 config["receivers"] 는 **항상** 포함됩니다.
    - config["receivers_by_type"][report_type] 에 적힌 주소는 **추가** 수신자로 합쳐집니다.
    - 대소문자 무시로 중복을 제거하며, 최초 등장 순서를 유지합니다.

    예) receivers=[A, B], receivers_by_type.morning=[C, D] 이면
        morning 수신자는 [A, B, C, D] 가 된다. (공통 A·B 는 종류와 무관하게 항상 수신)

    receivers_by_type 가 없는 구버전 email.json 은 공통 receivers 만 사용되어
    기존과 동일하게 동작한다(하위 호환).
    """
    result: list = []
    seen: set = set()

    def _add(items) -> None:
        for r in _clean_list(items):
            key = r.lower()
            if key not in seen:
                seen.add(key)
                result.append(r)

    _add(config.get("receivers"))  # 공통 수신자 (항상 포함)
    by_type = config.get("receivers_by_type")
    if report_type and isinstance(by_type, dict):
        _add(by_type.get(report_type))  # 종류별 추가 수신자
    return result


def _mask_secret(text) -> str:
    """오류 메시지에 앱 비밀번호가 섞여 노출되지 않도록 마스킹하고 길이를 제한한다."""
    out = str(text or "")
    for key in ("GMAIL_APP_PASSWORD", "SMTP_PASS", "SMTP_PASSWORD"):
        val = os.environ.get(key)
        if val and val in out:
            out = out.replace(val, "***")
    return out[:1500]


def _report_email_failure_to_github(report_type, subject, recipients, error) -> None:
    """
    이메일 전송 실패 정보를 전용 GitHub 이슈에 댓글로 누적 기록한다.

    Gmail SMTP(앱 비밀번호 GMAIL_APP_PASSWORD) 인증/네트워크 문제로 발송이 실패하면,
    운영자가 놓치지 않도록 실패 시각·리포트 종류·수신자·오류 내용을 이슈에 남긴다.
    기록 자체가 파이프라인을 멈추지 않도록 모든 예외를 흡수한다.
    """
    owner = os.environ.get("GITHUB_OWNER")
    repo = os.environ.get("GITHUB_REPO")
    token = os.environ.get("GITHUB_TOKEN")
    if not all([owner, repo, token]):
        debug_log("이메일 실패 GitHub 이슈 등록 건너뜀: GITHUB_OWNER/REPO/TOKEN 미설정")
        return
    try:
        from datetime import datetime
        from zoneinfo import ZoneInfo
        from .github_issue import find_or_create_issue, create_comment

        issue_no = find_or_create_issue(
            owner, repo, token,
            title="🚨 이메일 전송 실패 로그 (Email Delivery Failures)",
            label="email-failure",
        )
        ts = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S KST")
        recips = list(recipients or [])
        pw_source = next(
            (k for k in ("GMAIL_APP_PASSWORD", "SMTP_PASS", "SMTP_PASSWORD") if os.environ.get(k)),
            "(미설정)",
        )
        body = (
            "## ❌ 이메일 전송 실패\n\n"
            f"- **발생 시각**: {ts}\n"
            f"- **리포트 종류**: {report_type or '(미지정)'}\n"
            f"- **제목**: {subject or '(없음)'}\n"
            f"- **수신자({len(recips)}명)**: {', '.join(recips) if recips else '(미확인)'}\n"
            f"- **사용한 비밀번호 시크릿**: `{pw_source}`\n"
            f"- **오류 내용**:\n\n```\n{_mask_secret(error)}\n```\n\n"
            "> 🔑 Gmail SMTP 인증 실패라면 `GMAIL_APP_PASSWORD` 시크릿(16자리 앱 비밀번호)의 "
            "유효성, 발송 계정의 2단계 인증·앱 비밀번호 재발급 여부, 그리고 시크릿이 "
            "repo Settings → Secrets and variables → Actions 에 정확히 등록됐는지 확인하세요."
        )
        create_comment(owner, repo, token, issue_no, body)
        debug_log(f"이메일 전송 실패를 GitHub 이슈 #{issue_no}에 기록했습니다.")
    except Exception as ge:  # noqa: BLE001 - 기록 실패가 파이프라인을 멈추지 않도록
        debug_log(f"이메일 실패 GitHub 이슈 등록 실패(무시): {ge}")


def send_email_report(subject: str, content: str, report_type: str | None = None) -> None:
    """
    Gmail SMTP를 사용하여 email.json에 등록된 설정 및 수신자들로 이메일을 발송합니다.
    - Markdown → HTML 변환 후 multipart/alternative 형식으로 발송
    - plain text 폴백 포함 (HTML 미지원 클라이언트 대응)
    - [FIX] 수신자 전체를 단일 sendmail()로 발송하여 중복 수신 방지

    report_type: "morning" | "evening" | "consolidated" (선택).
        지정 시 해당 타입 전용 스위치(_REPORT_TYPE_ENV)로 발송 여부를 추가 제어한다.
        마스터 스위치(ENABLE_EMAIL_SENDER=1)가 켜져 있어야 하며, 타입 스위치는
        기본 활성이고 값이 '0'일 때만 해당 타입 발송을 건너뛴다.
    """
    enable_sender = os.environ.get("ENABLE_EMAIL_SENDER") == "1"
    if not enable_sender:
        debug_log("이메일 전송 기능이 비활성화 상태입니다. (ENABLE_EMAIL_SENDER != 1)")
        return

    if not _is_report_type_enabled(report_type):
        env_key = _REPORT_TYPE_ENV.get(report_type or "", "")
        debug_log(f"'{report_type}' 타입 이메일 전송이 비활성화 상태입니다. ({env_key}=0)")
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

    if not sender:
        print("[ERROR] email.json 내에 발신자 주소(sender)가 설정되지 않았습니다.")
        return

    # 리포트 종류별 수신자 결정 (receivers_by_type[type] → 없으면 공통 receivers 폴백)
    clean_receivers = _resolve_receivers(config, report_type)
    if not clean_receivers:
        print(
            f"[WARNING] email.json 내에 '{report_type}' 타입 및 공통(receivers) "
            "수신자 목록이 모두 비어 있습니다."
        )
        return

    # Gmail 앱 비밀번호 획득 (환경 변수 - GitHub Secrets)
    # 신규 이름 GMAIL_APP_PASSWORD 우선, 구 이름(SMTP_PASS/SMTP_PASSWORD)은 전환기 폴백.
    smtp_password = (
        os.environ.get("GMAIL_APP_PASSWORD")
        or os.environ.get("SMTP_PASS")
        or os.environ.get("SMTP_PASSWORD")
    )
    if not smtp_password:
        msg = "Gmail 앱 비밀번호(GMAIL_APP_PASSWORD 환경변수)가 설정되지 않았습니다."
        print(f"[ERROR] {msg}")
        _report_email_failure_to_github(report_type, subject, clean_receivers, msg)
        return

    debug_log(f"이메일 발송 작업을 시작합니다. (타입: {report_type}, 수신인: {clean_receivers})")

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
        return True  # 실제 발송 성공 시에만 True (호출부의 멱등 마커 등에 사용)
    except Exception as e:
        print(f"[ERROR] 이메일 전송 중 SMTP 서버 오류 발생: {e}")
        _report_email_failure_to_github(
            report_type, subject, clean_receivers, f"{type(e).__name__}: {e}"
        )
        return False
