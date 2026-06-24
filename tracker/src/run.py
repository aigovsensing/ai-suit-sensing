from __future__ import annotations
import os
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from .fetch import fetch_news
from .extract import load_known_cases, build_lawsuits_from_news
from .render import render_markdown
from .github_issue import find_or_create_issue, create_comment, close_other_daily_issues
from .github_issue import list_comments
from .slack import post_to_slack
from .utils import debug_log, slugify_case_name
from .dedup import apply_deduplication
from .courtlistener import (
    search_recent_documents,
    build_complaint_documents_from_hits,
    build_case_summaries_from_hits,
    build_case_summaries_from_docket_numbers,
    build_case_summaries_from_case_titles,
    build_documents_from_docket_ids,
)
from .queries import COURTLISTENER_QUERIES
from .trend import generate_trend_summary
from .gemini import get_gemini_model_display_name
from .email_sender import send_email_report, get_subject_for_report

def main() -> None:
    # 0) 환경 변수 로드
    owner = os.environ.get("GITHUB_OWNER")
    repo = os.environ.get("GITHUB_REPO")
    gh_token = os.environ.get("GITHUB_TOKEN")
    slack_webhook = os.environ.get("SLACK_WEBHOOK_URL")

    if not all([owner, repo, gh_token, slack_webhook]):
        missing = [k for k, v in {"GITHUB_OWNER": owner, "GITHUB_REPO": repo, "GITHUB_TOKEN": gh_token, "SLACK_WEBHOOK_URL": slack_webhook}.items() if not v]
        raise ValueError(f"필수 환경 변수가 누락되었습니다: {', '.join(missing)}")

    base_title = os.environ.get("ISSUE_TITLE_BASE", "AI 소송 모니터링")
    lookback_days = int(os.environ.get("LOOKBACK_DAYS", "3"))
    # 필요 시 2로 변경: 환경변수 LOOKBACK_DAYS=2
    
    # KST 기준 날짜 생성
    now_kst = datetime.now(ZoneInfo("Asia/Seoul"))
    run_ts_kst = now_kst.strftime("%Y-%m-%d %H:%M")
    weekdays_en = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekday_str = weekdays_en[now_kst.weekday()]
    issue_day_kst = f"{now_kst.strftime('%Y-%m-%d')} {weekday_str}"
    issue_title = f"{base_title} ({issue_day_kst})"
    debug_log(f"KST 기준 실행시각: {run_ts_kst}")
    
    issue_label = os.environ.get("ISSUE_LABEL", "ai-lawsuit-monitor")

    # 1) CourtListener 검색
    hits = []
    for q in COURTLISTENER_QUERIES:
        debug_log(f"Running CourtListener query: {q}")
        hits.extend(search_recent_documents(q, days=lookback_days, max_results=20))
    
    # 중복 제거
    dedup = {}
    for h in hits:
        key = (h.get("absolute_url") or h.get("url") or "") + "|" + (h.get("caseName") or h.get("title") or "")
        dedup[key] = h
    hits = list(dedup.values())

    cl_docs = build_complaint_documents_from_hits(hits, days=lookback_days)
    # RECAP 도켓(사건) 요약: "법원 사건(도켓) 확인 건수"로 사용
    cl_cases = build_case_summaries_from_hits(hits)

    # 2) 뉴스 수집
    news = fetch_news()
    known = load_known_cases()
    lawsuits = build_lawsuits_from_news(news, known, lookback_days=lookback_days)

    # 2-1) 뉴스 테이블의 소송번호(도켓번호)로 RECAP 도켓/문서 확장
    docket_numbers = [s.case_number for s in lawsuits if (s.case_number or "").strip() and s.case_number != "미확인"]
    extra_cases = build_case_summaries_from_docket_numbers(docket_numbers)

    # 2-2) 소송번호가 없더라도, '소송제목'(추정 케이스명)으로 도켓 확장
    case_titles = [s.case_title for s in lawsuits if (s.case_title or "").strip() and s.case_title != "미확인"]
    extra_cases_by_title = build_case_summaries_from_case_titles(case_titles)

    merged_cases = {c.docket_id: c for c in (cl_cases + extra_cases + extra_cases_by_title)}
    cl_cases = list(merged_cases.values())

    # 문서도 docket id 기반으로 추가 시도(Complaint 우선, 없으면 fallback)
    docket_ids = list(merged_cases.keys())
    extra_docs = build_documents_from_docket_ids(docket_ids, days=lookback_days)
    merged_docs = {}
    for d in (cl_docs + extra_docs):
        key = (d.docket_id, d.doc_number, d.date_filed, d.document_url)
        merged_docs[key] = d
    cl_docs = list(merged_docs.values())

    docket_case_count = len(cl_cases)
    
    # =====================================================
    # FIX: RECAP 문서 건수 계산 방식 수정
    # 해결: cl_docs에 있는 것 + cl_cases 중 complaint_link가 있는 Docket ID 합산
    # =====================================================
    unique_dockets_with_docs = set()
    for d in cl_docs:
        if d.docket_id:
            unique_dockets_with_docs.add(d.docket_id)
    for c in cl_cases:
        if c.complaint_link and c.docket_id:
            unique_dockets_with_docs.add(c.docket_id)
    
    recap_doc_count = len(unique_dockets_with_docs)

    # =====================================================
    # NEW: DEBUG 모드 및 데이터 유무에 따른 실행 구조 개선
    # - DEBUG=1: 데이터가 없어도 항상 출력 (디버깅용)
    # - DEBUG=0 (기본): 데이터(News, Cases)가 모두 0건이면 출력/통지 건너뜀
    # =====================================================
    is_debug = os.environ.get("DEBUG") == "1"
    if not is_debug and len(lawsuits) == 0 and docket_case_count == 0:
        debug_log(f"데이터가 없으며 DEBUG=0이므로 리포트 생성 및 전송을 건너뜁니다. (News: 0, Cases: 0)")
        return

    # 3) 렌더링
    md = render_markdown(
        lawsuits,
        cl_docs,
        cl_cases,
        recap_doc_count,
        lookback_days=lookback_days,
    )



    # 4) GitHub Issue 작업
    issue_no = find_or_create_issue(owner, repo, gh_token, issue_title, issue_label)

    issue_url = f"https://github.com/{owner}/{repo}/issues/{issue_no}"

    # =========================================================
    # Baseline 비교 로직 (매 댓글 실시간 중복 제거 강화)
    # =========================================================
    # 1. 현재 이슈의 기존 댓글 (오늘 이미 보고된 내용 확인)
    current_comments = list_comments(owner, repo, gh_token, issue_no)
    
    # 2. 이전 이슈들의 댓글도 베이스라인에 포함 (Cross-Issue 연속성 유지)
    # [Mission] PREVIOUS_ITEM_DEDUP_DAYS 설정 기간만큼 이전 이슈들을 탐색하여 중복 필터링
    from .github_issue import list_issues_by_label
    
    dedup_days_str = os.environ.get("PREVIOUS_ITEM_DEDUP_DAYS")
    prev_comments = []
    
    if dedup_days_str:
        try:
            dedup_days = int(dedup_days_str)
            debug_log(f"최근 {dedup_days}개 이전 이슈를 베이스라인으로 사용하여 중복을 필터링합니다.")
            
            recent_issues = list_issues_by_label(owner, repo, gh_token, issue_label, state="all", per_page=dedup_days + 5)
            # 현재 이슈보다 번호가 작은 이슈들만 필터링
            other_issues = [it for it in recent_issues if int(it["number"]) < issue_no]
            other_issues.sort(key=lambda x: int(x["number"]), reverse=True)
            
            # 설정한 일수만큼 이전 이슈 탐색
            for it in other_issues[:dedup_days]:
                p_no = int(it["number"])
                debug_log(f"이전 이슈 #{p_no}의 댓글을 베이스라인에 추가합니다.")
                prev_comments.extend(list_comments(owner, repo, gh_token, p_no))
        except ValueError:
            debug_log(f"유효하지 않은 PREVIOUS_ITEM_DEDUP_DAYS 값: {dedup_days_str}. 이전 이슈 중복 체크를 건너뜁니다.")
    else:
        debug_log("PREVIOUS_ITEM_DEDUP_DAYS가 설정되지 않았습니다. 이전 이슈와의 중복 체크를 수행하지 않습니다.")
        
    # 오늘 수집된 댓글 + 어제 최종 댓글들을 모두 합쳐서 중복 제거 기준으로 사용
    all_baseline_comments = current_comments + prev_comments
    
    md, new_news_count, new_cases_count = apply_deduplication(md, all_baseline_comments)
    
    # 새로운 소식이 하나도 없는지 여부 확인
    no_new_updates = (new_news_count == 0 and new_cases_count == 0)

    if no_new_updates:
        md = "새로운 소식들이 없습니다."
    else:
        # 실행 시각(KST)을 상단에 배치
        md = f"## 🖥️ 비인가 데이터 학습 소송 모니터링 (실행시각: {run_ts_kst} KST)\n\n" + md

    # 이전 날짜 이슈 Close
    closed_nums = close_other_daily_issues(owner, repo, gh_token, issue_label, base_title, issue_title, issue_no, issue_url)
    if closed_nums:
        debug_log(f"이전 날짜 이슈 자동 Close: {closed_nums}")
    
    debug_log(f"📊 수집 및 분석 완료 (최근 {lookback_days}일)")
    debug_log(f"  ├ News: {len(lawsuits)}건")
    debug_log(f"  └ Cases (CourtListener+RECAP): {docket_case_count}건 (문서 {recap_doc_count}건)")

    # 4-2) Gemini를 통한 핵심 동향 요약 추가 (첫 번째 댓글로 등록)
    # [Mission] 첫 번째 리포트(댓글이 없는 경우)이거나 새로운 소식이 있는 경우 Gemini 분석 수행
    trend_lookback = os.environ.get("GEMINI_AISUIT_TREND_DAYS")
    if trend_lookback:
        try:
            # 숫자가 아닌 값이 들어올 경우(예: 'true', 'on') lookback_days를 기본값으로 사용
            try:
                trend_days = int(trend_lookback)
            except ValueError:
                trend_days = lookback_days
                debug_log(f"GEMINI_AISUIT_TREND_DAYS가 숫자가 아니므로 LOOKBACK_DAYS({lookback_days})를 사용합니다.")

            # [FIX] 해당 기간(trend_days)의 동향 요약이 이미 있는지 확인 (중복 출력 방지 및 설정 변경 반영)
            trend_title_marker = f"{trend_days}일간의 소송센싱 주요 동향 현황"
            trend_already_exists = any(trend_title_marker in (c.get("body") or "") for c in current_comments)

            if not trend_already_exists:
                debug_log(f"Gemini 동향 요약 기능 활성화 (설정 기간: {trend_days}일)")
                trend_summary = generate_trend_summary(lawsuits, cl_cases, trend_days)
                if trend_summary:
                    create_comment(owner, repo, gh_token, issue_no, trend_summary)
                    debug_log(f"Issue #{issue_no} Gemini 동향 요약 댓글 업로드 완료")
                    # 이메일 발송
                    try:
                        email_subject = get_subject_for_report(trend_summary, "morning", trend_days)
                        send_email_report(email_subject, trend_summary)
                    except Exception as email_err:
                        print(f"[ERROR] 조간뉴스 이메일 발송 중 예외 발생: {email_err}")
        except Exception as e:
            debug_log(f"Gemini 동향 요약 생성 중 오류 발생: {e}")
    else:
        # 이미 안내 메시지나 동향 요약이 있는지 확인
        trend_any_exists = any("소송센싱 주요 동향 현황" in (c.get("body") or "") for c in current_comments)
        if not trend_any_exists:
            skip_message = (
                "> [!NOTE]\n"
                "> **🤖 Gemini 인텔리전트 동향 요약 기능 안내**\n"
                f"> \"🗓️ (조간뉴스) {lookback_days}일간의 소송센싱 주요 동향 현황\"이 Skip 처리되었습니다. \n"
                "> 이 기능을 사용하려면 [README.md](./README.md) 파일을 참고하여 관련 환경변수를 추가해 주세요. ✨"
            )
            create_comment(owner, repo, gh_token, issue_no, skip_message)
            debug_log("Gemini 동향 요약 Skip 안내 메시지 등록 완료")

    # 4-3) 통계 및 추이 리포트 추가 (옵션)
    if os.environ.get("GENERATE_STATS") == "1":
        from .stats import generate_trend_report
        # 통계 리포트가 이미 오늘 등록되었는지 확인 (중복 방지)
        stats_already_exists = any("AI 소송 발생 건수 추이 보고서" in (c.get("body") or "") for c in current_comments)
        if not stats_already_exists:
            debug_log("통계 및 추이 리포트 생성 중...")
            stats_report = generate_trend_report()
            create_comment(owner, repo, gh_token, issue_no, stats_report)
            debug_log(f"Issue #{issue_no} 통계 리포트 댓글 업로드 완료")

    # 4-4) 메인 리포트 등록 (마지막 댓글로 등록)
    comment_body = f"\n\n{md}"
    create_comment(owner, repo, gh_token, issue_no, comment_body)
    debug_log(f"Issue #{issue_no} 메인 리포트 댓글 업로드 완료")

    # 5) Slack 요약 전송
    # ============================================
    # Slack 출력 개선 (최종 포맷)
    # ============================================
    timestamp = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M KST")

    slack_dedup_news = None
    slack_dedup_cases = None

    if "### 중복 제거 요약:" in md:
        m_news = re.search(
            r"└ News (.+)",
            md,
        )

        m_cases = re.search(
            r"└ Cases (.+)",
            md,
        )

        if m_news:
            line = m_news.group(1).strip()
            # GitHub용 강조(**)와 🔴 제거 (Slack용으로 재구성하기 위함)
            line = line.replace("**", "").replace(" 🔴", "")
            # New 수치가 0보다 크면 강조 (Bolding + 🔴)
            slack_dedup_news = re.sub(
                r"(\d+)\s+\(New\)",
                lambda m: f"*{m.group(1)} (New)*" + (" :red_circle:" if int(m.group(1)) > 0 else ""),
                line
            )

        if m_cases:
            line = m_cases.group(1).strip()
            # GitHub용 강조(**)와 🔴 제거
            line = line.replace("**", "").replace(" 🔴", "")
            slack_dedup_cases = re.sub(
                r"(\d+)\s+\(New\)",
                lambda m: f"*{m.group(1)} (New)*" + (" :red_circle:" if int(m.group(1)) > 0 else ""),
                line
            )



    if no_new_updates:
        # 새로운 소식이 없는 경우 아주 간단하게 전송
        slack_body = "새로운 소식들이 없습니다."
    else:
        slack_lines = []

        slack_lines.append(":bar_chart: AI 소송 모니터링")
        slack_lines.append(f"🕒 {timestamp}")
        slack_lines.append("")

        # 🔁 Dedup Summary
        if slack_dedup_news and slack_dedup_cases:
            slack_lines.append(":arrows_counterclockwise: Dedup Summary")
            slack_lines.append(f"└ News {slack_dedup_news}")
            slack_lines.append(f"└ Cases {slack_dedup_cases}")
            slack_lines.append("")

        # 📈 Collection Status
        slack_lines.append(":chart_with_upwards_trend: Collection Status")
        slack_lines.append(f"└ News: {len(lawsuits)}")
        slack_lines.append(
            f"└ Cases: {docket_case_count} (Docs: {recap_doc_count})"
        )
        slack_lines.append("")

        # 🔗 GitHub
        slack_lines.append(f":link: GitHub: <{issue_url}|#{issue_no}>")

        # 🆕 최신 RECAP 문서 (820 Copyright) - Top 3
        copyright_cases = []
        for c in cl_cases:
            nos = str(c.nature_of_suit or "").strip()
            if "820" in nos or "copyright" in nos.lower():
                copyright_cases.append(c)

        top_cases = sorted(
            copyright_cases,
            key=lambda x: x.recent_updates if x.recent_updates != "미확인" else "",
            reverse=True
        )[:3]

        if top_cases:
            slack_lines.append("")
            slack_lines.append(":new: 최신 RECAP 문서 (820 Copyright)")

            for c in top_cases:
                date = c.recent_updates if c.recent_updates != "미확인" else "N/A"
                name = c.case_name
                # slug 생성 (utils의 공통 함수 사용)
                slug = slugify_case_name(name)
                docket_url = f"https://www.courtlistener.com/docket/{c.docket_id}/{slug}/"
                
                slack_lines.append(f"• {date} | <{docket_url}|{name}>")
        
        slack_body = "\n".join(slack_lines)

    try:
        post_to_slack(slack_webhook, slack_body)
        debug_log(f"Slack 전송 완료")
    except Exception as e:
        debug_log(f"Slack 전송 실패: {e}")
        
if __name__ == "__main__":
    main()
