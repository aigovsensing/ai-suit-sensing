#!/usr/bin/env python3
"""
generate_reports.py — AI 월간 보고서 정적 사전 생성기 (GitHub Pages 용)

백엔드(FastAPI)의 POST /api/report/generate 는 서버 + Gemini API 키가 필요해
정적 호스팅에서 실행할 수 없다. 대신 **빌드 시점(GitHub Actions)** 에 Gemini 로
월별 보고서를 미리 생성해 정적 JSON 으로 저장하면, 런타임에는 백엔드 없이도
프론트엔드가 해당 파일을 받아 그대로 표시할 수 있다.

출력:
    docs/api/report/<type>/<YYYY-MM>.json   = {"report": "<markdown>"}
    docs/api/report/manifest.json           = 캐시(입력 해시) — 변경분만 재생성

동작:
    - GEMINI_API_KEY 가 없으면 아무것도 하지 않고 정상 종료(exit 0).
      → 키 없는 로컬/포크 빌드에서도 사이트 빌드는 깨지지 않는다.
    - 최신 데이터셋(기본) 기준으로 각 report type 의 "데이터가 있는" 월을
      최신순 REPORT_MAX_MONTHS 개까지 생성한다.
    - 입력(해당 월 레코드 + 전체 통계) 해시가 이전과 같고 출력 파일이 있으면
      Gemini 호출을 건너뛴다(비용/쿼터 절약).

환경변수:
    GEMINI_API_KEY          (필수) Gemini API 키
    GEMINI_MODEL            1차 모델 (기본 gemini-flash-latest)
    GEMINI_MODEL_FALLBACKS  폴백 모델 CSV
    REPORT_TYPES            기본 "filing_date,last_update"
    REPORT_MAX_MONTHS       타입별 최신 N개월 (기본 24)
    REPORT_DATASET          특정 CSV 파일명(기본: 최신)

주의: 프롬프트/폴백 로직은 dashboard/backend/main.py 의 generate_report 와
      동일해야 한다. 백엔드를 수정하면 이 파일도 함께 갱신할 것.
"""
import argparse
import hashlib
import json
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.dirname(SCRIPT_DIR)
REPO_ROOT = os.path.dirname(DASHBOARD_DIR)
DATA_DIR = os.path.join(DASHBOARD_DIR, "data")

sys.path.insert(0, DASHBOARD_DIR)
import pandas as pd  # noqa: E402


# --- backend/main.py 와 동일한 폴백 체인 -----------------------------------
DEFAULT_FALLBACK_CHAIN = [
    "gemini-flash-latest",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]


def get_gemini_fallback_models():
    primary = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
    raw = os.environ.get("GEMINI_MODEL_FALLBACKS", "")
    fallbacks = [m.strip() for m in raw.split(",") if m.strip()] or DEFAULT_FALLBACK_CHAIN
    ordered = []
    for name in [primary, *fallbacks]:
        if name not in ordered:
            ordered.append(name)
    return ordered


def _is_transient_gemini_error(err) -> bool:
    e = str(err).lower()
    return any(
        s in e
        for s in ("429", "resource_exhausted", "500", "502", "503", "504", "unavailable", "internal")
    )


def find_col_in_df(keys, df):
    for k in keys:
        for col in df.columns:
            if k.lower() == col.lower():
                return col
    for k in keys:
        for col in df.columns:
            if k.lower() in col.lower():
                if k == "피고" and "원고" in col:
                    continue
                if k == "원고" and "피고" in col:
                    continue
                return col
    return None


def build_prompt(df, filtered_df, month):
    """backend/main.py generate_report 의 프롬프트를 그대로 구성한다."""
    total_cases_all = len(df)
    defendant_col = find_col_in_df(["피고", "Defendant", "피고*"], df)
    top_5_defendants = df[defendant_col].value_counts().head(5).to_dict() if defendant_col else {}

    date_col_year = find_col_in_df(["소송제기일", "Filing Date"], df)
    if date_col_year:
        yearly_series = pd.to_datetime(df[date_col_year], errors="coerce")
        yearly_trend = yearly_series.dt.year.value_counts().sort_index().to_dict()
    else:
        yearly_trend = {}

    case_summary = filtered_df.to_json(orient="records", force_ascii=False)

    prompt = f"""
첨부한 데이터는 {month} 기준 AI 데이터 소송 관련 데이터베이스입니다.
이 데이터를 바탕으로 전문적인 'AI 데이터 소송 월간 동향 보고서'를 작성해 주세요.

[제공된 데이터 - {month} 상세]
{case_summary}

[전체 데이터베이스 통계 정보]
- 전체 누적 소송 건수: {total_cases_all}
- 누적 피고 순위 Top 5: {top_5_defendants}
- 연도별 소송 증가 추이: {yearly_trend}

보고서에는 다음 항목이 반드시 포함되어야 합니다:

1. Executive Summary:
   - 해당 월({month})의 신규 소송 건수 요약.
   - 가장 핵심적인 법적 트렌드(예: TPM 우회, 저작권 침해, 무단 스크래핑 등) 요약.

2. 신규 소송 현황 분석:
   - 신규 소송의 총 건수, 주요 피고 기업, 국가별 분포를 표(Table)로 정리.
   - 소송 목록을 날짜순으로 정리하고, 각 소송의 핵심 쟁점(핵심 논거)을 기술.

3. 유형별 심층 분석:
   - 데이터에서 가장 높은 비중을 차지하는 소송 유형(예: YouTube 무단 스크래핑, 개인정보 침해 등)을 그룹화하여 분석.
   - 특정 기업(예: OpenAI, Google, Runway AI 등)에 소송이 집중된 경우 그 원인과 증거(내부 문서 유출 등)를 상세히 기술.

4. 글로벌 동향 및 특이 사례:
   - 미국 외 국가(유럽 GDPR, 한국 방송사 소송 등)에서 발생한 주요 소송의 의미 분석.
   - 퍼블리시티권이나 AI 음성 합성 같은 신규 소송 유형이 있다면 별도로 강조.

5. 통계 및 전망:
   - 전체 데이터베이스를 기준으로 한 연도별 소송 증가 추이와 누적 피고 순위 Top 5 도출.
   - 향후 법적 판결이 업계에 미칠 영향이나 주목해야 할 모니터링 포인트(Monitoring Points) 제시.

[보고서 형식 및 지침]
- 가독성을 위해 표(Table), 불렛 포인트, 섹션 구분을 명확히 사용하세요.
- 톤앤매너는 전문적인 기술 전략 보고서 스타일로 작성하세요.
- 한국어로 작성하고 마크다운(Markdown) 형식을 유지하세요.
- 별도의 대제목(## {month} 보고서 등)은 생략하고 바로 '1. Executive Summary'부터 시작하세요.
"""
    return prompt


def generate_one(genai, df, filtered_df, month):
    """Gemini 호출(재시도+폴백). 성공 시 markdown 문자열, 실패 시 None."""
    prompt = build_prompt(df, filtered_df, month)
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    max_retries = 3
    base_delay = 2.0
    last_error = None
    for current_model in get_gemini_fallback_models():
        for attempt in range(max_retries):
            try:
                model = genai.GenerativeModel(model_name=current_model, safety_settings=safety_settings)
                response = model.generate_content(prompt)
                if response.candidates and response.candidates[0].content.parts:
                    print(f"        ✓ {month} via {current_model}")
                    return response.text
                print(f"        ! {month}: 응답 차단/후보 없음")
                return None
            except Exception as e:  # noqa: BLE001
                last_error = e
                print(f"        … {month} (model={current_model}, try {attempt + 1}/{max_retries}): {e}")
                if _is_transient_gemini_error(e) and attempt < max_retries - 1:
                    time.sleep(base_delay * (2 ** attempt))
                    continue
                break
    print(f"        ✗ {month}: 모든 폴백 실패 ({last_error})")
    return None


def load_df(csv_path):
    df = pd.read_csv(csv_path, skiprows=2).fillna("")
    title_col = find_col_in_df(["소송제목 (원고 v. 피고)*", "소송제목 (원고 v. 피고)", "Case Name"], df)
    if title_col:
        df = df[df[title_col].astype(str).str.strip() != ""]
    return df


def month_input_hash(filtered_df, df):
    total = len(df)
    defc = find_col_in_df(["피고", "Defendant", "피고*"], df)
    top5 = df[defc].value_counts().head(5).to_dict() if defc else {}
    payload = filtered_df.to_json(orient="records", force_ascii=False) + json.dumps(
        {"total": total, "top5": top5}, ensure_ascii=False, sort_keys=True
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(REPO_ROOT, "docs"))
    args = ap.parse_args()
    docs = os.path.abspath(args.out)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[reports] GEMINI_API_KEY 미설정 → 보고서 사전 생성을 건너뜁니다(정상).")
        return 0

    try:
        import google.generativeai as genai
    except ImportError:
        print("[reports] google-generativeai 패키지가 없어 건너뜁니다. `pip install google-generativeai`")
        return 0
    genai.configure(api_key=api_key)

    types = [t.strip() for t in os.environ.get("REPORT_TYPES", "filing_date,last_update").split(",") if t.strip()]
    max_months = int(os.environ.get("REPORT_MAX_MONTHS", "24"))

    csv_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".csv")], reverse=True)
    if not csv_files:
        print("[reports] 데이터 CSV 없음")
        return 0
    dataset = os.environ.get("REPORT_DATASET") or csv_files[0]
    csv_path = os.path.join(DATA_DIR, dataset)
    print(f"[reports] 데이터셋: {dataset} | types={types} | max_months={max_months}")

    df = load_df(csv_path)

    report_root = os.path.join(docs, "api", "report")
    os.makedirs(report_root, exist_ok=True)
    manifest_path = os.path.join(report_root, "manifest.json")
    manifest = {}
    if os.path.exists(manifest_path):
        try:
            manifest = json.load(open(manifest_path, encoding="utf-8"))
        except Exception:
            manifest = {}

    date_cols = {
        "filing_date": ["소송제기일", "Filing Date"],
        "last_update": ["Last Update(업로드 시 제외)", "Last Update", "최근 업데이트"],
    }

    generated = skipped = failed = 0
    for rtype in types:
        col = find_col_in_df(date_cols.get(rtype, []), df)
        if not col:
            print(f"[reports] type={rtype}: 날짜 컬럼 없음 → 건너뜀")
            continue
        dser = pd.to_datetime(df[col], errors="coerce")
        months = sorted({m for m in dser.dt.strftime("%Y-%m").dropna() if m and m != "NaT"}, reverse=True)
        months = months[:max_months]
        out_dir = os.path.join(report_root, rtype)
        os.makedirs(out_dir, exist_ok=True)
        print(f"[reports] type={rtype} ({col}) → {len(months)}개월")

        dfm = df.copy()
        dfm[col] = pd.to_datetime(dfm[col], errors="coerce")
        for month in months:
            filtered = dfm[dfm[col].dt.strftime("%Y-%m") == month]
            if filtered.empty:
                continue
            out_path = os.path.join(out_dir, f"{month}.json")
            mkey = f"{rtype}/{month}"
            h = month_input_hash(filtered, df)
            if manifest.get(mkey) == h and os.path.exists(out_path):
                skipped += 1
                continue
            md = generate_one(genai, df, filtered, month)
            if md is None:
                failed += 1
                continue
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump({"report": md}, f, ensure_ascii=False)
            manifest[mkey] = h
            generated += 1

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=0)

    print(f"[reports] 완료: 생성 {generated} · 캐시적중 {skipped} · 실패 {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
