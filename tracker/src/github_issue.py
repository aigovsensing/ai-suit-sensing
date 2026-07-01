from __future__ import annotations
import re
import requests
from typing import Dict, List
from .dedup import generate_consolidated_report
from .email_sender import send_email_report, get_subject_for_report

def _headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

def find_or_create_issue(owner: str, repo: str, token: str, title: str, label: str) -> int:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    r = requests.get(url, headers=_headers(token), params={"state": "open", "labels": label, "per_page": 50}, timeout=20)
    r.raise_for_status()
    issues = r.json()
    for it in issues:
        if it.get("title") == title:
            return int(it["number"])
    payload = {
        "title": title,
        "body": (
            "## 📋 자동 수집 리포트\n\n"
            "이 이슈에는 자동 수집된 리포트가 댓글로 누적됩니다.\n\n"
            "---\n\n"
            "## 📡 데이터 수집 출처\n\n"
            "| 출처 | 설명 |\n"
            "|------|------|\n"
            "| **Google News RSS** | Google News에서 제공하는 RSS(Really Simple Syndication) 피드로, 특정 키워드나 주제에 대한 최신 뉴스를 자동으로 수집하고 구독할 수 있는 서비스입니다. |\n"
            "| **RECAP** | PACER(유료 미국 연방법원 전자기록 시스템)의 데이터를 무료로 접근하고 효율적으로 활용하기 위한 오픈소스 프로젝트입니다. 소송 데이터 수집·추출·분석에 초점을 맞추고 있습니다. |\n"
            "| **CourtListener** | RECAP 프로젝트를 통해 PACER 데이터를 수집·저장하여, 미국 연방 및 주 법원의 판결 기록을 무료로 검색하고 분석할 수 있도록 제공하는 플랫폼입니다. |\n\n"
            "<details>\n"
            "<summary><b>⚖️ 법률 코드 안내 (클릭하여 펼치기)</b></summary>\n\n"
            "### ⚖️ Nature of Suit (NOS) 및 Cause of Action (COA)코드 안내\n"
            "소송의 성격 및 사건 유형을 나타내는 코드입니다.\n\n"
            "| 분류체계 |NOS 코드 | 의미 |\n"
            "|:---:|---|---|\n"
            "| Nature of Suit | **820** | Copyright (저작권 사건) |\n"
            "| Nature of Suit | **3820** | Copyright Appeal (저작권 항소) |\n"
            "| Nature of Suit |**830** | Patent (특허) |\n"
            "| Nature of Suit |**840** | Trademark (상표) |\n"
            "| Nature of Suit |**190** | Contract: Other (기타 계약 분쟁) |\n"
            "| Nature of Suit |**410** | Antitrust (독점금지법) |\n"
            "| Nature of Suit |**442** | Civil Rights: Employment (고용 관련 시민권) |\n"
            "| Nature of Suit |**360** | Personal Injury: Other |\n"
            "| Cause of Action |**35:271** | Patent Infringement (특허 침해) |\n"
            "| Cause of Action |**15:1125** | Trademark Infringement (상표 침해) |\n"
            "| Cause of Action |**17:501** | Copyright Infringement (저작권 침해) |\n"
            "| Cause of Action |**17:101** | Copyright Infringement |\n"
            "| Cause of Action |**17:504** | Copyright Infringement |\n"
            "| Cause of Action |**17:505** | Copyright Infringement |\n"
            "| Cause of Action |**17:512** | Copyright Infringement (DMCA) |\n"
            "| Cause of Action |**17:1201** | Copyright Infringement (DMCA) |\n"
            "| Cause of Action |**17:1202** | Copyright Infringement (DMCA) |\n\n"
            "---\n\n"
            "> 💡 **참고:** 'Nature of Suit': 사건 유형, 'Cause of Action': 청구원인/법적근거.\n"
            "> \n"
            "> **COA 코드 해석 예시:**\n"
            "> - **35:271** → Title 35 (특허법), § 271 → 특허 침해 (가장 일반적인 특허 소송)\n"
            "> - **15:1125** → Title 15 (상거래법), § 1125 → 상표 침해 (Lanham Act)\n"
            "> - **17:501** → Title 17 (저작권법), § 501 → 저작권 침해\n"
            "</details>\n"
        ),
        "labels": [label]
    }    
    r2 = requests.post(url, headers=_headers(token), json=payload, timeout=20)
    r2.raise_for_status()
    return int(r2.json()["number"])

def create_comment(owner: str, repo: str, token: str, issue_number: int, body: str) -> None:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    r = requests.post(url, headers=_headers(token), json={"body": body}, timeout=20)
    r.raise_for_status()

def list_issues_by_label(owner: str, repo: str, token: str, label: str, state: str = "open", per_page: int = 50) -> list[dict]:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    r = requests.get(url, headers=_headers(token), params={"state": state, "labels": label, "per_page": per_page}, timeout=20)
    r.raise_for_status()
    return r.json() or []

def close_issue(owner: str, repo: str, token: str, issue_number: int) -> None:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    r = requests.patch(url, headers=_headers(token), json={"state": "closed"}, timeout=20)
    r.raise_for_status()

def close_other_daily_issues(owner: str, repo: str, token: str, label: str, base_title: str, today_title: str, new_issue_number: int, new_issue_url: str) -> list[int]:
    """같은 라벨을 가진 모니터링 이슈 중 '오늘/현재' 이슈를 제외한 나머지 OPEN 이슈를 닫습니다."""
    closed: list[int] = []
    issues = list_issues_by_label(owner, repo, token, label, state="open")
    prefix = f"{base_title} ("
    
    # [수정] footer 문자열을 올바르게 합치고 따옴표를 닫았습니다.
    footer = (
        f"다음 리포트: #{new_issue_number} ({new_issue_url})\n\n"
        "이 이슈는 다음 리포트 생성으로 자동 종료되었습니다."
    )

    for it in issues:
        t = it.get("title") or ""
        if t == today_title:
            continue
        # base_title (YYYY-MM-DD) 형태만 닫기
        if t.startswith(prefix) and t.endswith(")"):
            num = int(it["number"])
            
            # [추가] 이슈를 닫기 전에 모든 댓글을 취합하여 통합 리포트 작성 및 Gemini 분석
            try:
                comments = list_comments(owner, repo, token, num)
                
                # 1) 통합 리포트 (통계/테이블)
                consolidated_report = generate_consolidated_report(comments)
                create_comment(owner, repo, token, num, consolidated_report)
                
                # 2) 당일 신규/업데이트 소송건 요약 보고서(석간뉴스)
                # 저녁(21시) 실행에서 이미 당일 이슈에 석간뉴스를 발행했다면 중복 생성/발송하지 않는다.
                evening_already = any("(석간뉴스" in (c.get("body") or "") for c in comments)
                if evening_already:
                    import sys
                    print(f"[INFO] 이슈 #{num}에 석간뉴스가 이미 존재하여 Close 시 재생성을 건너뜁니다.", file=sys.stderr)
                else:
                    from .dedup import get_consolidated_data
                    from .trend import generate_daily_report_from_data
                    u_news, u_cases, _ = get_consolidated_data(comments)

                    # 석간뉴스 날짜는 '닫히는 이슈' 제목의 날짜와 동일해야 한다.
                    # 이슈 제목 형식: "{base_title} (YYYY-MM-DD Weekday)"
                    m_date = re.search(r"\d{4}-\d{2}-\d{2}", t)
                    report_date = m_date.group(0) if m_date else None

                    daily_summary = generate_daily_report_from_data(u_news, u_cases, report_date=report_date)
                    if daily_summary:
                        create_comment(owner, repo, token, num, daily_summary)
                        # 이메일 발송
                        try:
                            email_subject = get_subject_for_report(daily_summary, "evening")
                            send_email_report(email_subject, daily_summary)
                        except Exception as email_err:
                            import sys
                            print(f"[ERROR] 석간뉴스 이메일 발송 중 예외 발생: {email_err}", file=sys.stderr)
                
                # 3) 최종 종료 알림 (footer)
                final_body = f"--- \n\n{footer}"
            except Exception as e:
                import sys
                print(f"Error generating consolidated reports for issue #{num}: {e}", file=sys.stderr)
                final_body = footer

            comment_and_close_issue(owner, repo, token, num, final_body)
            closed.append(num)
    return closed

def comment_and_close_issue(owner: str, repo: str, token: str, issue_number: int, body: str) -> None:
    # 먼저 마무리 코멘트 작성
    url_c = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    rc = requests.post(url_c, headers=_headers(token), json={"body": body}, timeout=20)
    rc.raise_for_status()
    # 그 다음 이슈 Close
    close_issue(owner, repo, token, issue_number)



 
# =========================================================
# NEW: Issue 댓글 조회 (baseline 확보용)
# =========================================================
def list_comments(owner: str, repo: str, token: str, issue_number: int) -> list[dict]:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    r = requests.get(url, headers=_headers(token), timeout=20)
    r.raise_for_status()
    return r.json() or []




