import os
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List
from .extract import Lawsuit
from .courtlistener import CLCaseSummary
from .gemini import get_gemini_summary
from .utils import debug_log

def generate_trend_summary(lawsuits: List[Lawsuit], cl_cases: List[CLCaseSummary], lookback_days: int, report_date: str | None = None) -> str:
    """
    수집된 뉴스 및 소송 데이터를 기반으로 Gemini를 통해 주요 동향 요약을 생성합니다.
    """
    # 데이터 요약 구성 (출처 URL 포함)
    news_context = ""
    for idx, s in enumerate(lawsuits, 1):
        url = s.article_urls[0] if s.article_urls else ""
        news_context += f"{idx}. {s.update_or_filed_date} | {s.article_title or s.case_title} | {s.reason} | 출처: {url}\n"
    
    case_context = ""
    for idx, c in enumerate(cl_cases, 1):
        # slug 생성 (utils의 공통 함수 사용)
        from .utils import slugify_case_name
        slug = slugify_case_name(c.case_name)
        docket_url = f"https://www.courtlistener.com/docket/{c.docket_id}/{slug}/"
        case_context += f"{idx}. {c.recent_updates} | {c.case_name} | Nature: {c.nature_of_suit} | Snippet: {c.extracted_ai_snippet or ''} | 출처: {docket_url}\n"

    # 날짜는 GitHub 이슈 제목과 동일해야 하므로 호출부에서 전달받는다(없으면 KST 오늘로 폴백).
    today_kst = report_date or datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")

    prompt = f"""
당신은 AI 법률 및 저작권 전문 분석 Skill-Driven Agent입니다. 최근 {lookback_days}일 동안 발생한 AI 모델 학습 관련 데이터 이용 현황 및 주요 소송 건들을 객관적으로 분석하여 전문적인 보고서를 작성해주세요.

[보고서 구성 항목]
1. 개요: 최근 AI 기술과 데이터 저작권 관련 주요 동향의 전체적인 흐름 요약
2. 주요 소송 및 분석 현황: 제공된 데이터를 바탕으로 주요 소송 사건들의 사실 관계 및 현황 (주체, 사건명, 날짜, 주요 내용 등)
3. 주요 법적 논점 및 전망: 소송에서 다뤄지는 핵심 법리적 쟁점과 향후 소송 전개 방향 및 결과에 대한 예측
4. 시사점: 이러한 법적 동향이 AI 기술 생태계 및 관련 이해관계자들에게 시사하는 바와 고려해야 할 점
5. 삼성전자 관련 영향 분석: 삼성전자의 생성형 AI 모델(가우스 등), 서비스 또는 하드웨어 제품(갤럭시 AI 등)에 미칠 수 있는 영향, 기술적/법적 대비 사항 또는 전략적 고려 요소

[작성 지침]
1. 제목은 "## 🗓️ (조간뉴스: {today_kst}) {lookback_days}일간의 AI학습데이터 소송 동향"으로 시작해주세요. (날짜 {today_kst} 는 반드시 그대로 포함)
2. 사실에 기반하여 객관적이고 차분한 분석 톤을 유지해주세요.
3. 각 소송 항목에는 가능한 경우 제공된 데이터의 '출처'를 마크다운 링크 형식으로 포함해주세요 (예: [출처 이름](URL)).
4. 제공된 데이터를 우선적으로 활용하되, 학습된 지식과 최신 정보를 바탕으로 내용을 심도 있게 구성해주세요.

[제공된 데이터 - 뉴스]
{news_context or "최근 수집된 뉴스가 없습니다."}

[제공된 데이터 - 법원 소송]
{case_context or "최근 수집된 법원 소송 데이터가 없습니다."}
"""

    debug_log(f"Gemini 동향 요약 생성 중 (데이터: 뉴스 {len(lawsuits)}건, 소송 {len(cl_cases)}건)")
    summary = get_gemini_summary(prompt)
    
    if not summary:
        return ""
        
    return summary.strip()

def generate_daily_report_from_data(news_data: dict, case_data: dict, report_date: str | None = None) -> str:
    """
    당일 취합된 뉴스 및 소송 데이터를 기반으로 Gemini를 통해 당일 리포트를 요약합니다.
    (취합 댓글 분석용)
    """
    news_lines = []
    for k, r in news_data.items():
        news_lines.append(f"- {r[1]} | {r[2]} | {r[5]} (감지레벨: {r[6]})")
    
    case_lines = []
    for k, r in case_data.items():
        # r[2]는 케이스명, r[3]은 도켓번호, r[4]는 Nature, r[6]은 소송이유, r[5]는 감지레벨
        case_lines.append(f"- {r[2]} (도켓: {r[3]}) | Nature: {r[4]} | 소송이유: {r[6]} (감지레벨: {r[5]})")

    # 날짜는 닫히는 GitHub 이슈 제목과 동일해야 하므로 호출부에서 전달받는다(없으면 KST 오늘로 폴백).
    today_kst = report_date or datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")

    prompt = f"""
당신은 AI 법률 및 저작권 전문 분석 Skill-Driven Agent입니다. '오늘(오늘 하루 동안 수합된 리포트)' 수집된 다음의 AI 관련 뉴스 및 소송 사건들을 분석하여, 핵심 내용을 요약하는 "당일 신규/업데이트 소송건 요약 보고서"를 작성해주세요.

[분석 대상 데이터]
- 뉴스:
{chr(10).join(news_lines) if news_lines else "오늘 수집된 뉴스가 없습니다."}

- 소송:
{chr(10).join(case_lines) if case_lines else "오늘 수집된 소송 사건이 없습니다."}

[작성 지침]
1. 제목은 "## 🧠 (석간뉴스: {today_kst}) 당일 AI학습데이터 소송건 요약"으로 시작해주세요. (날짜 {today_kst} 는 반드시 그대로 포함)
2. 오늘 발생한 가장 중요한 핵심 이슈를 2~3문장으로 먼저 요약해주세요.
3. 주요 뉴스 및 소송 사건들을 그룹화하거나 개별적으로 분석하여 가독성 있게 정리해주세요.
4. 기술적/법적 쟁점이 있는 경우 간략히 언급해주세요.
5. 말투는 전문적이고 객관적인 어조를 유지하며, 한국어로 작성해주세요.
6. 제공된 데이터에 기반하되, 전문적인 통찰력을 담아주세요.
"""
    debug_log(f"Gemini 당일 요약 리포트 생성 중 (데이터: 뉴스 {len(news_lines)}건, 소송 {len(case_lines)}건)")
    summary = get_gemini_summary(prompt)
    if not summary:
        # GEMINI_API_KEY가 설정되지 않은 경우 (get_gemini_summary가 "" 반환)
        summary = f"## 🧠 (석간뉴스: {today_kst}) 당일 AI학습데이터 소송건 요약\n\n> [!CAUTION]\n> **보고서 요약 실패:** GEMINI_API_KEY가 설정되지 않아 요약 보고서를 생성할 수 없습니다.\n"
    # get_gemini_summary()가 API 오류 발생 시 이미 에러 메시지를 포함한 경고 마크다운을 반환하므로 별도 처리 불필요
    
    # [추가] 지브리 스타일 이미지 생성 제어 (환경 변수 확인)
    image_gen_enabled = os.environ.get("GEMINI_DAILY_REPORT_IMAGEGEN") == "1"
    
    if not image_gen_enabled:
        return summary.strip()

    from .gemini import generate_gemini_image
    
    # 요약문의 첫 번째 단락이나 핵심 요약을 바탕으로 프롬프트 추출 (간단히 핵심 요약 활용)
    visual_prompt = "AI and Copyright Lawsuit theme"
    if "**[금일 핵심 요약]**" in summary:
        try:
            visual_prompt = summary.split("**[금일 핵심 요약]**")[1].split("\n")[0].strip()
        except:
            pass
            
    # 이미지 저장 경로 (github actions 실행 시 docs/img 폴더에 저장하여 커밋 연동 고려)
    img_dir = "docs/img"
    img_path = os.path.join(img_dir, "daily_visual_report.png")
    
    debug_log(f"지브리 스타일 이미지 생성 시도 (프롬프트: {visual_prompt})")
    saved_path, error_msg = generate_gemini_image(visual_prompt, img_path)
    
    if saved_path:
        # GitHub Repo 내의 이미지를 참조하도록 링크 구성
        owner = os.environ.get("GITHUB_OWNER", "OWNER")
        repo = os.environ.get("GITHUB_REPO", "REPO")
        img_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/docs/img/daily_visual_report.png"
        
        image_section = f"""

### 4. 🎨 시각적 동향 리포트 (Ghibli Style)
![AI Lawsuit Ghibli Style]({img_url})

> **[AI 이미지 가이드]** 위 이미지는 금일 핵심 이슈를 바탕으로 생성된 지브리 스타일의 일러스트입니다. (이미지가 보이지 않는 경우, 워크플로우에서 `docs/img` 폴더의 변경사항을 커밋하도록 설정했는지 확인해주세요.)
"""
        return summary.strip() + image_section
    else:
        # 이미지 생성 실패 시 오류 메시지 추가 (사용자 요청사항)
        fail_msg = f"\n\n> [!WARNING]\n> **이미지 생성 실패:** {error_msg if error_msg else '알 수 없는 오류'} 이슈 때문에 이미지 생성을 실패했습니다. 텍스트 리포트만 출력합니다.\n"
        return summary.strip() + fail_msg
