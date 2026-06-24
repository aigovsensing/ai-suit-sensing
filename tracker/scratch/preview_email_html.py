"""
이메일 HTML 변환 미리보기 테스트
실행: python scratch/preview_email_html.py
→ scratch/email_preview.html 생성 후 브라우저로 확인
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 실제 email_sender 내부 함수 가져오기
from src.email_sender import _markdown_to_html, _HTML_TEMPLATE, _extract_title_line

SAMPLE_MARKDOWN = """
## 🗓️ (조간뉴스) 3일간의 소송센싱 주요 동향 현황

모델 정보: gemini-2.5-flash  서비스 티어: Standard

> [!NOTE]
> 이 보고서는 Gemini AI가 자동 생성한 요약본입니다.

---

### 1. 개요

최근 3일간(2026년 6월 21일 ~ 6월 23일) 관찰된 AI 모델 학습 관련 데이터 이용 현황 및 주요 소송 건들을 분석합니다.

### 2. 주요 소송 및 분석 현황

#### 2.1. 엔비디아(NVIDIA) 대상 음악 저작권 침해소송

* **주제제**: S.A. Jamendo (음악 플랫폼) vs. NVIDIA Corporation
* **사건명**: S.A. JAMENDO v. NVIDIA Corporation
* **날짜**: 2026-06-23

> [!WARNING]
> Jamendo가 엔비디아야기자사의 AI 모델 학습을 위해 저작권이 없는 음악 데이터를 대량으로 수집하여 저작권을 침해했다고 주장하며 소송을 제기했습니다.

#### 2.2. 음악 저작권 관련 소송 현황

| 사건명 | 원고 | 피고 | 상태 |
|--------|------|------|------|
| Jamendo v. NVIDIA | Jamendo | NVIDIA | 진행 중 |
| Doe v. OpenAI | 작가 그룹 | OpenAI | 항소 중 |
| Getty v. Stability AI | Getty Images | Stability AI | 심리 중 |

### 3. 주요 법적 논점 및 전망

1. **학습 데이터 이용의 공정 사용(Fair Use) 해당 여부**가 핵심 쟁점입니다.
2. AI 기업들은 학습 데이터 이용이 변혁적 사용(Transformative Use)에 해당한다고 주장합니다.
3. 법원은 아직 이에 대한 명확한 판결을 내리지 않고 있습니다.

### 4. 시사점

* 저작권자의 권리 보호 요구가 강화되고 있습니다.
* AI 기업들은 학습 데이터 수집 및 이용 방식에 대한 법적 리스크를 면밀히 검토해야 합니다.

### 5. 삼성전자 관련 영향 분석

삼성전자의 **가우스(Gauss)** 및 **갤럭시 AI** 관련 서비스는 유사한 법적 리스크에 노출될 수 있습니다.

> [!CAUTION]
> 삼성전자는 생성형 AI 모델의 학습 데이터 출처 및 이용 라이선스를 재검토하고, 저작권 침해 가능성을 사전 차단하는 컴플라이언스 체계를 강화할 필요가 있습니다.
"""

subject = '[ai.gov.sensing] "(조간뉴스) 3일간의 소송센싱 주요 동향 현황"'
title_line = _extract_title_line(subject, SAMPLE_MARKDOWN)
body_html  = _markdown_to_html(SAMPLE_MARKDOWN)
full_html  = _HTML_TEMPLATE.format(
    subject    = subject,
    title_line = title_line,
    body_html  = body_html,
)

out_path = os.path.join(os.path.dirname(__file__), "email_preview.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(full_html)

print(f"✅ HTML 미리보기 생성 완료: {out_path}")
print("   브라우저에서 해당 파일을 열어 이메일 레이아웃을 확인하세요.")
