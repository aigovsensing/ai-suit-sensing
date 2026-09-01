from __future__ import annotations
"""
조간/석간 리포트 본문 조립 모듈.

리포트는 항상 아래 3개 카테고리 구조로 일관되게 조립된다:

  1. (Gemini) 당일 AI 학습데이터 소송 건 요약   ← gemini_md (호출부에서 전달)
  2. (Google Alert) 국내외 기사 모니터링         ← news_digest
  3. (courtlistener.com) 신규 소송 제기 현황     ← new_lawsuits

GitHub 이슈 본문과 이메일 본문은 대부분 동일하지만, "2. 기사 모니터링"의 '더보기'
처리만 다르다(GitHub=<details> 접기, 이메일=상위 N건 + 이슈 링크). 따라서 뉴스는
한 번만 수집(collect_daily_news)한 뒤 두 버전으로 렌더링하여 두 본문을 함께 만든다.
"""
from typing import List, Optional, Tuple

from .news_digest import collect_daily_news, render_daily_news_section
from .new_lawsuits import build_new_lawsuits_section
from .dataset_status import build_dataset_status_section


def _join(*parts: str) -> str:
    return "\n\n---\n\n".join(p for p in parts if p and p.strip())


def assemble_digest(
    gemini_md: str,
    report_date: Optional[str] = None,
    cl_lookback_days: Optional[int] = None,
    issue_url: Optional[str] = None,
    hits: Optional[List[dict]] = None,
) -> Tuple[str, str]:
    """
    (github_body, email_body) 튜플을 반환한다.

    Args:
        gemini_md: "1." 카테고리(Gemini 요약) 마크다운. 제목 라인(조간/석간 마커)을 포함해야
            이메일 제목/헤더 추출이 정상 동작한다.
        report_date: 표기용 날짜(YYYY-MM-DD).
        cl_lookback_days: "3. 신규 소송"의 Date Filed 기준 기간(일). 미지정 시 env LOOKBACK_DAYS.
        issue_url: 이메일 "2." 섹션에서 '전체 목록'을 안내할 GitHub 이슈 URL.
        hits: run.py 등이 이미 수행한 CourtListener 검색 결과. 있으면 재사용해 중복 호출 방지.
    """
    # 2. 뉴스 모니터링 — 한 번 수집 → GitHub/이메일 두 버전 렌더
    news_data = collect_daily_news(report_date=report_date)
    news_github = render_daily_news_section(news_data, for_email=False)
    news_email = render_daily_news_section(news_data, for_email=True, issue_url=issue_url)

    # 3. 신규 소송 제기 현황 — GitHub/이메일 공통(접기 불필요)
    new_suits = build_new_lawsuits_section(
        report_date=report_date, lookback_days=cl_lookback_days, hits=hits
    )

    # 4. 소송사건에 연관된 데이터셋 현황 — 리포트 제일 마지막(GitHub/이메일 공통)
    # 검색 스니펫뿐 아니라 Gemini/기사 본문도 함께 검사한다. CourtListener 스니펫에
    # 데이터셋 이름이 잘려 있더라도 앞 섹션에 명시된 이름을 최종 현황에서 보존한다.
    dataset_source_text = _join(gemini_md, news_github, new_suits)
    dataset_status = build_dataset_status_section(
        hits,
        dataset_source_text,
        header="## 4. 🧬 소송사건에 연관된 데이터셋 현황",
    )

    github_body = _join(gemini_md, news_github, new_suits, dataset_status)
    email_body = _join(gemini_md, news_email, new_suits, dataset_status)
    return github_body, email_body
