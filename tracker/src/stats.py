import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .courtlistener import get_search_count
from .utils import debug_log

def get_historical_data():
    """
    2021년부터 현재까지의 연도별 AI 소송 건수를 조회합니다.
    """
    years = [2021, 2022, 2023, 2024, 2025, 2026]
    # 대표적인 AI 학습 관련 쿼리
    query = '("AI training" OR "model training" OR "training data" OR dataset OR LLM) (copyright OR DMCA OR unauthorized OR scraping)'
    results = {}
    
    debug_log("연도별 통계 데이터 수집 시작...")
    for year in years:
        count = get_search_count(f"{query} dateFiled:[{year}-01-01 TO {year}-12-31]")
        results[year] = count
        debug_log(f" - {year}년: {count}건")
    
    return results

def generate_trend_report():
    """
    소송 추이 그래프를 생성하고 마크다운 리포트를 반환합니다.
    """
    try:
        data = get_historical_data()
        years = list(data.keys())
        counts = list(data.values())

        # 1) Matplotlib 그래프 생성
        plt.figure(figsize=(10, 6))
        plt.plot(years, counts, marker='o', linestyle='-', color='#007bff', linewidth=3, markersize=8)
        plt.fill_between(years, counts, alpha=0.1, color='#007bff')
        
        # 스타일 설정
        plt.title('AI Litigation Trends (US Federal Courts)', fontsize=18, fontweight='bold', pad=20)
        plt.xlabel('Year', fontsize=12, labelpad=10)
        plt.ylabel('Number of Lawsuits', fontsize=12, labelpad=10)
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.xticks(years)
        
        # 건수 레이블 추가
        for i, count in enumerate(counts):
            plt.text(years[i], counts[i] + (max(counts)*0.02), str(count), ha='center', fontweight='bold')

        # 이미지 저장
        os.makedirs('img', exist_ok=True)
        img_filename = 'lawsuit_trend.png'
        img_path = os.path.join('img', img_filename)
        plt.savefig(img_path, dpi=150, bbox_inches='tight')
        plt.close()
        debug_log(f"추이 그래프 저장 완료: {img_path}")

        # 2) Mermaid 차트 생성 (GitHub 렌더링용)
        mermaid = "```mermaid\nxychart-beta\n"
        mermaid += "    title \"AI Litigation Trends (Yearly)\"\n"
        mermaid += f"    x-axis {years}\n"
        mermaid += f"    y-axis \"Lawsuits\"\n"
        mermaid += f"    bar {counts}\n"
        mermaid += f"    line {counts}\n"
        mermaid += "```\n"

        # 3) 마크다운 리포트 구성
        report = (
            "## 📈 AI 소송 발생 건수 추이 보고서 (2021-2026)\n\n"
            "AI 시대가 본격화됨에 따라 비인가 데이터 학습 및 저작권 관련 소송이 급격히 증가하고 있는 추세를 확인할 수 있습니다.\n\n"
            "### 📊 연도별 추이 그래프\n\n"
            f"![AI 소송 추이 그래프](./img/{img_filename})\n\n"
            "#### [Mermaid Visualizer]\n"
            f"{mermaid}\n\n"
            "| 연도 | 소송 건수 (US Federal) | 비고 |\n"
            "|------|-----------------------|------|\n"
        )
        
        for year in years:
            trend = "▲" if year > 2021 and data[year] > data[year-1] else "-"
            report += f"| {year} | {data[year]} | {trend} |\n"
        
        report += "\n> [!NOTE]\n"
        report += "> 위 통계는 미국 연방법원(CourtListener/RECAP)에 등록된 소송 데이터를 기준으로 산출되었습니다. 전세계 국가별 세부 추이는 데이터 소스 확장에 따라 순차적으로 업데이트될 예정입니다.\n"

        return report

    except Exception as e:
        debug_log(f"통계 리포트 생성 중 오류 발생: {e}")
        return "⚠️ 통계 리포트 생성 중 오류가 발생하였습니다."
