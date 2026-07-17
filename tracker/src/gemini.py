import os
import time
from typing import List, Optional, Tuple
from google import genai
from google.genai import types
from .utils import debug_log

# 무료 티어 폴백 체인: 품질 우선(최신 3.x) → 안정성(무료 쿼터가 큰 2.5) 순으로 내려간다.
# 1차 모델이 429(쿼터 소진) 또는 사용 불가일 때 순차적으로 다음 모델로 폴백한다.
DEFAULT_FALLBACK_CHAIN = [
    "gemini-flash-latest",   # → 최신 Flash(현재 3.5)로 자동 해석
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",      # 무료 쿼터 큼(~250 RPD)
    "gemini-2.5-flash-lite", # 무료 쿼터 가장 큼(~1,000 RPD)
]

def get_gemini_model_name() -> str:
    """
    환경 변수에서 사용할 Gemini 모델명을 가져옵니다. 기본값은 'gemini-flash-latest'입니다.
    """
    return os.environ.get("GEMINI_MODEL", "gemini-flash-latest")

def get_gemini_fallback_models() -> List[str]:
    """
    순차적으로 시도할 후보 모델 리스트를 반환합니다.

    - 1차 모델은 `GEMINI_MODEL`(기본 'gemini-flash-latest').
    - 폴백 체인은 `GEMINI_MODEL_FALLBACKS`(쉼표 구분)로 재정의할 수 있으며,
      미지정 시 DEFAULT_FALLBACK_CHAIN 을 사용합니다.
    - 1차 모델을 맨 앞에 두고 중복을 제거해 순서를 보존합니다.
    """
    primary = get_gemini_model_name()

    raw = os.environ.get("GEMINI_MODEL_FALLBACKS", "")
    fallbacks = [m.strip() for m in raw.split(",") if m.strip()] or DEFAULT_FALLBACK_CHAIN

    ordered: List[str] = []
    for name in [primary, *fallbacks]:
        if name not in ordered:
            ordered.append(name)
    return ordered

def get_gemini_model_display_name() -> str:
    """
    출력용으로 친숙한 모델 이름을 반환합니다.
    """
    model_name = get_gemini_model_name()
    if "gemini-3.5" in model_name.lower():
        return "Gemini 3.5 Flash"
    if "gemini-3-flash" in model_name.lower() or "gemini-flash" in model_name.lower():
        return "Gemini 3 Flash"
    if "gemini-2.5-flash" in model_name.lower():
        return "Gemini 2.5 Flash"
    if "gemini-2.0-flash" in model_name.lower():
        return "Gemini 2.0 Flash"
    if "gemini-1.5-pro" in model_name.lower() or "gemini-pro" in model_name.lower():
        return "Gemini 1.5 Pro"
    
    # 환경변수에 직접 'Gemini 2.5 Flash' 처럼 넣었을 경우를 위해
    if "-" not in model_name and not model_name.islower():
        return model_name
        
    return "Gemini"

def get_gemini_summary(prompt: str) -> str:
    """
    Gemini API를 사용하여 텍스트 요약을 생성합니다.
    rate limit 및 transient 503 오류가 발생할 경우를 위해 exponential backoff와 fallback model을 포함하고 있습니다.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        debug_log("GEMINI_API_KEY가 설정되지 않아 Gemini 요약을 건너뜁니다.")
        return ""

    model_name = get_gemini_model_name()
    max_retries = 3
    base_delay = 2.0  # seconds
    
    # 순차적으로 시도할 후보 모델 리스트 (1차 → 폴백 체인)
    models_to_try = get_gemini_fallback_models()

    last_error = None
    final_model = model_name

    for current_model in models_to_try:
        final_model = current_model
        client = genai.Client(api_key=api_key)
        
        # 법률 데이터 분석 중 차단을 방지하기 위해 최소화된 필터를 설정합니다.
        safety_settings = [
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
        ]

        for attempt in range(max_retries):
            try:
                debug_log(f"Gemini API 호출 시도 (모델: {current_model}, 시도: {attempt + 1}/{max_retries})")
                
                response = client.models.generate_content(
                    model=current_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        safety_settings=safety_settings
                    )
                )

                if response.text:
                    model_version = getattr(response, "model_version", None) or current_model
                    
                    service_tier = "Standard"
                    usage_obj = getattr(response, "usage_metadata", None)
                    if usage_obj:
                        tier_val = getattr(usage_obj, "service_tier", None)
                        if tier_val and str(tier_val).lower() != "none":
                            service_tier = str(tier_val).capitalize()

                    debug_log(f"Gemini Metadata 추출 결과 - model_version: {model_version}, service_tier: {service_tier}")
                    
                    header = f"모델 정보: {model_version}\n서비스 티어: {service_tier}\n\n"
                    return header + response.text
                else:
                    raise ValueError("응답 텍스트가 비어 있거나 차단되었습니다.")

            except Exception as e:
                last_error = e
                debug_log(f"Gemini API 호출 오류 발생: {e}")
                
                # Rate limit (429) 또는 일시적인 서버 오류 (500, 503, 504) 여부 파악
                is_transient = False
                err_lower = str(e).lower()
                if "429" in err_lower or "resource_exhausted" in err_lower:
                    is_transient = True
                    debug_log("Rate limit (429 / RESOURCE_EXHAUSTED) 감지.")
                elif "503" in err_lower or "unavailable" in err_lower:
                    is_transient = True
                    debug_log("Service Unavailable (503) 감지.")
                elif "500" in err_lower or "504" in err_lower or "internal" in err_lower:
                    is_transient = True
                    debug_log("Internal Server Error (500 / 504) 감지.")

                if is_transient and attempt < max_retries - 1:
                    sleep_time = base_delay * (2 ** attempt)
                    debug_log(f"{sleep_time}초 후 재시도합니다...")
                    time.sleep(sleep_time)
                else:
                    # 일시적이지 않은 오류거나 재시도 횟수를 초과한 경우 루프 탈출 후 다음 모델 시도
                    break

    # 모든 재시도 및 백업 모델 호출마저 실패한 경우: 투명하게 에러 경고 마크다운 작성
    error_msg = str(last_error) if last_error else "알 수 없는 오류"

    # 에러 메시지에서 핵심 정보(code, message)만 추출하여 가독성 있는 요약 생성
    import re
    short_error = error_msg
    try:
        code_match = re.search(r"'code':\s*(\d+)", error_msg)
        msg_match = re.search(r"'message':\s*'([^']+)'", error_msg)
        if not msg_match:
            # 큰따옴표로 감싸인 경우도 처리
            msg_match = re.search(r'"message":\s*"([^"]+)"', error_msg)
        if code_match or msg_match:
            code_str = code_match.group(1) if code_match else ""
            msg_str = msg_match.group(1).split("\n")[0].strip() if msg_match else ""
            short_error = f"code: {code_str}, message: {msg_str}" if code_str else msg_str
    except Exception:
        pass  # 파싱 실패 시 원본 에러 메시지 사용

    title = ""
    if "조간뉴스" in prompt:
        title = "## 🗓️ (조간뉴스) 동향 요약 생성 실패\n\n"
    elif "석간뉴스" in prompt:
        title = "## 🧠 (석간뉴스) 당일 요약 보고서 생성 실패\n\n"

    warning_section = (
        f"{title}"
        "> [!CAUTION]\n"
        "> **🤖 Gemini API 호출 실패**\n"
        "> Gemini API 호출에 실패하거나 응답이 차단되어 요약 보고서를 자동 생성할 수 없습니다.\n"
        f"> - **최종 시도 모델**: `{final_model}`\n"
        f"> - **오류 정보**: `{short_error}`\n"
        "> \n"
        "> Rate Limit 초과 또는 구글 API 서버의 일시적인 혼잡/점검 상태일 수 있습니다. 잠시 후 워크플로우를 재실행해 보세요. ✨\n"
    )
    return warning_section

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Gemini API를 사용하여 텍스트 리스트의 임베딩을 생성합니다.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or not texts:
        return []

    try:
        client = genai.Client(api_key=api_key)
        # 최신 고성능 모델인 gemini-embedding-2를 기본 사용합니다.
        response = client.models.embed_content(
            model="models/gemini-embedding-2",
            contents=texts,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT"
            )
        )
        embeddings = []
        if response.embeddings:
            for emb in response.embeddings:
                embeddings.append(emb.values)
        return embeddings
    except Exception as e:
        debug_log(f"Gemini 임베딩(gemini-embedding-2) 생성 중 오류 발생: {e}")
        # fallback으로 gemini-embedding-001 사용
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.embed_content(
                model="models/gemini-embedding-001",
                contents=texts,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT"
                )
            )
            embeddings = []
            if response.embeddings:
                for emb in response.embeddings:
                    embeddings.append(emb.values)
            return embeddings
        except Exception as e2:
            debug_log(f"Gemini 임베딩 fallback(gemini-embedding-001) 생성 중 오류 발생: {e2}")
            return []

def calculate_cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """
    두 벡터 간의 코사인 유사도를 계산합니다.
    """
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = sum(a * a for a in v1) ** 0.5
    norm_v2 = sum(a * a for a in v2) ** 0.5
    
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    
    return dot_product / (norm_v1 * norm_v2)

def generate_gemini_image(prompt: str, output_path: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Google AI Studio의 Imagen 3 모델을 사용하여 이미지를 생성하고 저장합니다.
    Returns: (saved_path, error_message)
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        msg = "GEMINI_API_KEY가 설정되지 않아 이미지 생성을 건너뜀."
        debug_log(msg)
        return None, msg

    try:
        client = genai.Client(api_key=api_key)
        
        # 지브리 스타일을 위한 프롬프트 강화
        enhanced_prompt = f"Studio Ghibli anime style illustration, {prompt}. Hand-drawn aesthetic, lush colors, whimsical lighting, detailed scenery, painterly texture."
        
        debug_log(f"이미지 생성 시도: {enhanced_prompt}")
        
        response = client.models.generate_images(
            model='imagen-3.0-generate-001',
            prompt=enhanced_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type='image/png',
                add_watermark=False
            )
        )

        if response.generated_images:
            img = response.generated_images[0]
            # output_path가 폴더인 경우 파일명 생성
            if os.path.isdir(output_path):
                from datetime import datetime
                filename = f"daily_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                output_path = os.path.join(output_path, filename)
            
            # 폴더 생성
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 이미지 저장
            with open(output_path, "wb") as f:
                f.write(img.image.image_bytes)
            
            debug_log(f"이미지 저장 완료: {output_path}")
            return output_path, None
            
        return None, "이미지가 생성되었으나 응답 데이터가 비어 있습니다."
    except Exception as e:
        error_msg = str(e)
        debug_log(f"Gemini 이미지 생성 중 오류 발생: {error_msg}")
        return None, error_msg
