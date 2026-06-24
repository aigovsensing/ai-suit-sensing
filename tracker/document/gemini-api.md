# 🤖 Gemini API 사용 가이드

> **대상**: Google Gemini API를 활용하여 AI 기반 텍스트 요약 및 이미지 생성을 수행하는 방법을 학습합니다.  
> **관련 파일**: [`src/gemini.py`](../src/gemini.py), [`src/trend.py`](../src/trend.py)

---

## 1. Gemini API란?

Google Gemini API는 Google DeepMind의 멀티모달 AI 모델 **Gemini**에 접근하기 위한 REST API입니다.

- **공식 문서**: https://ai.google.dev/docs
- **콘솔**: https://aistudio.google.com
- **무료 티어**: Gemini 2.0 Flash 기준 분당 15회 요청 (무료)
- **Python SDK**: `google-generativeai` 또는 `google-genai`

---

## 2. API 키 발급

1. [https://aistudio.google.com](https://aistudio.google.com) 접속
2. 구글 계정으로 로그인
3. 왼쪽 메뉴 **"Get API key"** 클릭
4. **"Create API key"** 클릭
5. 키 복사 → GitHub Secrets에 `GEMINI_API_KEY`로 등록

---

## 3. 주요 모델

| 모델명 | 특징 | 용도 |
|--------|------|------|
| `gemini-2.5-flash` | 빠른 응답, 저비용 | **이 프로젝트에서 사용** |
| `gemini-2.5-pro` | 고성능, 복잡한 추론 | 심층 분석 |
| `gemini-2.0-flash` | 구세대 Flash | 기존 호환성 |
| `gemini-1.5-pro` | 긴 컨텍스트 지원 | 대용량 문서 분석 |

---

## 4. Python으로 Gemini 사용하기

### 설치

```bash
pip install google-generativeai
# 또는 신 SDK
pip install google-genai
```

### 기본 텍스트 생성

```python
import google.generativeai as genai

# API 키 설정
genai.configure(api_key="YOUR_API_KEY")

# 모델 초기화
model = genai.GenerativeModel("gemini-2.5-flash")

# 텍스트 생성
response = model.generate_content("AI 저작권 소송의 핵심 쟁점을 3줄로 요약해줘.")
print(response.text)
```

### 이 프로젝트에서의 활용 ([`src/gemini.py`](../src/gemini.py))

```python
import os
import google.generativeai as genai

def get_gemini_summary(prompt: str) -> str:
    """Gemini를 통해 텍스트 요약을 생성합니다."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return ""

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"[ERROR] Gemini API 오류: {e}")
        return ""
```

---

## 5. 프롬프트 설계 (이 프로젝트)

### 조간뉴스 프롬프트 ([`src/trend.py`](../src/trend.py))

```python
prompt = f"""
당신은 AI 법률 및 저작권 전문 분석 Skill-Driven Agent입니다.
최근 {lookback_days}일 동안 발생한 AI 모델 학습 관련 데이터 이용 현황 및 주요 소송 건들을 분석하여
전문적인 보고서를 작성해주세요.

[보고서 구성 항목]
1. 개요: 전체적인 흐름 요약
2. 주요 소송 및 분석 현황
3. 주요 법적 논점 및 전망
4. 시사점
5. 삼성전자 관련 영향 분석

[작성 지침]
1. 제목은 "## 🗓️ (조간뉴스) {lookback_days}일간의 소송센싱 주요 동향 현황"으로 시작

[제공된 데이터 - 뉴스]
{news_context}

[제공된 데이터 - 법원 소송]
{case_context}
"""
```

### 석간뉴스 프롬프트

```python
prompt = f"""
당신은 AI 법률 및 저작권 전문 분석 Skill-Driven Agent입니다.
오늘 수집된 AI 관련 뉴스 및 소송 사건들을 분석하여 핵심 내용을 요약하는
"당일 신규/업데이트 소송건 요약 보고서"를 작성해주세요.

[작성 지침]
1. 제목은 "## 🧠 (석간뉴스) 당일 신규/업데이트 소송건 요약 보고서 (Gemini)"로 시작
2. 오늘 발생한 가장 중요한 핵심 이슈를 2~3문장으로 먼저 요약
3. 주요 뉴스 및 소송 사건들을 그룹화하거나 개별적으로 분석
4. 기술적/법적 쟁점 간략 언급
5. 전문적이고 객관적인 어조, 한국어로 작성
"""
```

---

## 6. 토큰 및 비용

### 토큰 계산
- 1 토큰 ≈ 영어 약 4글자, 한국어 약 2~3글자
- `gemini-2.5-flash`: 입력 $0.075/1M 토큰, 출력 $0.30/1M 토큰

### 무료 티어 한도 (2024 기준)
| 항목 | Gemini 2.0 Flash |
|------|-----------------|
| 분당 요청 (RPM) | 15 |
| 일일 요청 (RPD) | 1,500 |
| 분당 토큰 (TPM) | 1,000,000 |

---

## 7. Google AI Studio (웹 인터페이스)

[https://aistudio.google.com](https://aistudio.google.com)에서 브라우저로 Gemini를 직접 테스트할 수 있습니다.

**주요 기능**:
- **Prompt** 탭: 텍스트 프롬프트 테스트
- **Chat** 탭: 대화형 인터페이스
- **Stream** 탭: 스트리밍 응답 확인
- **Tune** 탭: 파인튜닝
- **Settings**: 온도(Temperature), Top-P, Max Tokens 조정

---

## 8. 참고 자료

| 링크 | 설명 |
|------|------|
| [Google AI Studio](https://aistudio.google.com) | API 키 발급 및 테스트 |
| [Gemini API 문서](https://ai.google.dev/docs) | 공식 문서 |
| [google-generativeai PyPI](https://pypi.org/project/google-generativeai/) | Python SDK |
| [Gemini 모델 목록](https://ai.google.dev/models/gemini) | 사용 가능한 모델 |
