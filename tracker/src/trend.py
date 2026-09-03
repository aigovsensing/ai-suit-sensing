import os
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List
from .extract import Lawsuit
from .courtlistener import CLCaseSummary
from .gemini import get_gemini_summary
from .utils import debug_log


def _morning_fallback(lawsuits, cl_cases, lookback_days, report_date):
    """외부 생성형 API 없이 수집 사실만으로 만드는 안전한 조간 요약."""
    news = []
    for item in lawsuits[:10]:
        label = item.article_title or item.case_title or "제목 미확인"
        url = item.article_urls[0] if item.article_urls else ""
        link = f"[{label}]({url})" if url else label
        news.append(f"* **{link}**\n  * 내용: {item.reason or '세부 내용 확인 필요'}\n  * 시사점: 원문과 사건 기록을 교차 확인해야 합니다.")
    cases = []
    for item in cl_cases[:10]:
        cases.append(f"* **{item.case_name}** (도켓 {item.docket_number or '미확인'}, Nature: {item.nature_of_suit or '미확인'})\n  * 공개 도켓의 최근 업데이트를 추적해야 합니다.")
    return f"""## 🗓️ (조간뉴스: {report_date}) {lookback_days}일간의 AI학습데이터 소송 동향

## 1. 최근 {lookback_days}일간 AI 학습데이터 소송 동향 요약 (출처: 수집 데이터 자동 정리)

### 📝 핵심 요약 (3문장)
최근 {lookback_days}일 동안 관련 뉴스 {len(lawsuits)}건과 신규·갱신 도켓 {len(cl_cases)}건이 수집되었습니다. 아래 내용은 수집 원문과 법원 공개 도켓을 기준으로 자동 정리되었습니다. 법적 판단이나 위험 평가는 연결된 원문을 확인한 뒤 수행해야 합니다.

### 1.1 글로벌 주요 뉴스 및 판결 분석
{chr(10).join(news) if news else '* 최근 수집된 관련 뉴스가 없습니다.'}

### 1.2 신규 접수 주요 소송 동향 (미 연방법원 도켓 분석)
{chr(10).join(cases) if cases else '* 제공된 신규 도켓 데이터가 없습니다.'}

### 1.3 법적·기술적 분석가 종합 통찰 (Insight)
* 수집 결과는 사건 발생 여부를 알리는 모니터링 자료이며, 청구의 인용이나 위법 확정을 뜻하지 않습니다.
* **삼성전자 영향/대비:** 가우스·갤럭시 AI 관련 학습 데이터의 출처, 라이선스, 삭제 이력을 지속적으로 문서화하고 유사 사건의 판결 변화를 점검해야 합니다.
"""


def _daily_fallback(news_data, case_data, report_date):
    """외부 생성형 API 장애 시에도 이메일 본문을 완성하는 당일 요약."""
    news = [f"* **{r[1] or '제목 미확인'}** — {r[2] or '내용 확인 필요'} (감지레벨: {r[6] or '미분류'})" for r in news_data.values()]
    cases = [f"* **{r[2] or '사건명 미확인'}** (도켓 {r[3] or '미확인'}, Nature: {r[4] or '미확인'}) — {r[6] or '소송이유 확인 필요'}" for r in case_data.values()]
    return f"""## 🧠 (석간뉴스: {report_date}) 당일 AI학습데이터 소송건 요약

## 1. 당일 AI 학습데이터 소송 건 요약 (출처: 수집 데이터 자동 정리)

### 📝 핵심 요약 (3문장)
오늘 관련 뉴스 {len(news_data)}건과 소송 {len(case_data)}건이 취합되었습니다. 아래 목록은 취합 데이터에 기재된 사실을 자동 정리한 결과입니다. 세부 분석과 의사결정 전에는 원문 및 법원 기록을 확인해야 합니다.

### 1.1 글로벌 주요 뉴스 및 판결 분석
{chr(10).join(news) if news else '* 오늘 수집된 뉴스가 없습니다.'}

### 1.2 신규 접수 주요 소송 동향 (미 연방법원 도켓 분석)
{chr(10).join(cases) if cases else '* 제공된 신규 도켓 데이터가 없습니다.'}

### 1.3 법적·기술적 분석가 종합 통찰 (Insight)
* 자동 정리 결과는 법률 의견이 아니며 사건 원문에 따른 후속 검토가 필요합니다.
* **삼성전자 영향/대비:** 가우스·갤럭시 AI의 데이터 계보와 라이선스 증빙을 보존하고 관련 소송의 쟁점 변화를 정기적으로 반영해야 합니다.
"""

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

[출력 형식 — 아래 마크다운 구조를 반드시 정확히 그대로 따르세요]
아래 제목과 소제목(##, ###)을 글자 하나 바꾸지 말고 그대로 사용하고, 각 소제목 아래에 내용을 채워주세요.

## 🗓️ (조간뉴스: {today_kst}) {lookback_days}일간의 AI학습데이터 소송 동향

## 1. 최근 {lookback_days}일간 AI 학습데이터 소송 동향 요약 (출처: Gemini)

### 📝 핵심 요약 (3문장)
(최근 {lookback_days}일간 가장 중요한 흐름을 정확히 3문장으로 요약)

### 1.1 글로벌 주요 뉴스 및 판결 분석
(해외/국내 주요 뉴스·판결을 "* " 불릿 목록으로. 각 항목은 굵은 제목 + 하위 불릿으로 '내용'과 '시사점'을 구분해 작성. 가능하면 감지레벨(🔥/⚠️/🟡/🟢)을 함께 표기)

### 1.2 신규 접수 주요 소송 동향 (미 연방법원 도켓 분석)
(제공된 소송 데이터를 그룹화하여 "* " 불릿 목록으로. 각 항목에 사건명·도켓번호(Nature 포함)와 간단한 분석을 작성. 데이터가 없으면 "제공된 신규 도켓 데이터가 없습니다."라고 적기)

### 1.3 법적·기술적 분석가 종합 통찰 (Insight)
(핵심 법리 쟁점과 향후 전망을 "* " 불릿으로 정리하고, 마지막에 반드시 삼성전자(가우스, 갤럭시 AI 등)에 미칠 영향/대비사항을 별도 불릿으로 포함)

[작성 지침]
1. 위 제목 라인 "## 🗓️ (조간뉴스: {today_kst}) {lookback_days}일간의 AI학습데이터 소송 동향"은 날짜 {today_kst} 와 기간 표기 "{lookback_days}일간의"를 포함하여 반드시 그대로 첫 줄에 출력하세요.
2. 위에 명시된 소제목(## 1. / ### 📝 / ### 1.1 / ### 1.2 / ### 1.3)만 사용하고, 임의의 다른 상위 번호(2., 3. 등)는 절대 만들지 마세요.
3. 사실에 기반하여 객관적이고 차분한 분석 톤을 유지하고, 각 항목에는 가능한 경우 '출처'를 마크다운 링크([이름](URL)) 형식으로 포함하세요.
4. 제공된 데이터를 우선적으로 활용하되, 학습된 지식과 최신 정보를 바탕으로 내용을 심도 있게 구성하세요.

[제공된 데이터 - 뉴스]
{news_context or "최근 수집된 뉴스가 없습니다."}

[제공된 데이터 - 법원 소송]
{case_context or "최근 수집된 법원 소송 데이터가 없습니다."}
"""

    debug_log(f"Gemini 동향 요약 생성 중 (데이터: 뉴스 {len(lawsuits)}건, 소송 {len(cl_cases)}건)")
    fallback = _morning_fallback(lawsuits, cl_cases, lookback_days, today_kst)
    summary = get_gemini_summary(prompt, fallback_text=fallback)
    
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

[출력 형식 — 아래 마크다운 구조를 반드시 정확히 그대로 따르세요]
아래 제목과 소제목(##, ###)을 글자 하나 바꾸지 말고 그대로 사용하고, 각 소제목 아래에 내용을 채워주세요.

## 🧠 (석간뉴스: {today_kst}) 당일 AI학습데이터 소송건 요약

## 1. 당일 AI 학습데이터 소송 건 요약 (출처: Gemini)

### 📝 핵심 요약 (3문장)
(오늘 가장 중요한 핵심 이슈를 정확히 3문장으로 요약)

### 1.1 글로벌 주요 뉴스 및 판결 분석
(해외/국내 주요 뉴스·판결을 "* " 불릿 목록으로. 각 항목은 굵은 제목 + 하위 불릿으로 '내용'과 '시사점'을 구분해 작성. 가능하면 감지레벨(🔥/⚠️/🟡/🟢)을 함께 표기)

### 1.2 신규 접수 주요 소송 동향 (미 연방법원 도켓 분석)
(제공된 소송 데이터를 그룹화하여 "* " 불릿 목록으로. 각 항목에 사건명·도켓번호(Nature 포함)와 간단한 분석을 작성. 데이터가 없으면 "제공된 신규 도켓 데이터가 없습니다."라고 적기)

### 1.3 법적·기술적 분석가 종합 통찰 (Insight)
(핵심 법리 쟁점과 향후 전망을 "* " 불릿으로 정리하고, 마지막에 반드시 삼성전자(가우스, 갤럭시 AI 등)에 미칠 영향/대비사항을 별도 불릿으로 포함)

[작성 지침]
1. 위 제목 라인 "## 🧠 (석간뉴스: {today_kst}) 당일 AI학습데이터 소송건 요약"은 날짜 {today_kst} 를 포함하여 반드시 그대로 첫 줄에 출력하세요.
2. 위에 명시된 소제목(## 1. / ### 📝 / ### 1.1 / ### 1.2 / ### 1.3)만 사용하고, 임의의 다른 상위 번호(2., 3. 등)는 절대 만들지 마세요.
3. 각 항목에는 가능한 경우 제공된 데이터의 '출처'를 마크다운 링크([이름](URL)) 형식으로 포함하세요.
4. 말투는 전문적이고 객관적인 어조를 유지하며, 한국어로 작성하세요.
5. 제공된 데이터에 기반하되, 학습된 지식과 전문적인 통찰력을 담아 심도 있게 구성하세요.
"""
    debug_log(f"Gemini 당일 요약 리포트 생성 중 (데이터: 뉴스 {len(news_lines)}건, 소송 {len(case_lines)}건)")
    fallback = _daily_fallback(news_data, case_data, today_kst)
    summary = get_gemini_summary(prompt, fallback_text=fallback)
    if not summary:
        summary = fallback
    
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
