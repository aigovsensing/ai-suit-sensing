# src/queries.py
# 균형형(소송 전반) CourtListener 쿼리: RECAP(=PACER Document) + complaint/petition 우선 + AI 학습/무단데이터 키워드
# 주의: CourtListener Search 문법/필드 지원은 서버 버전에 따라 일부 차이가 있을 수 있습니다.
COURTLISTENER_QUERIES = [
    'document_type:"PACER Document" (short_description:complaint OR short_description:"amended complaint" OR short_description:petition) ("AI training" OR "model training" OR "training data" OR dataset OR LLM OR "large language model") (copyright OR DMCA OR unauthorized OR pirated OR scraping OR "without permission")',
    'document_type:"PACER Document" (short_description:complaint OR short_description:"amended complaint") (Anthropic OR OpenAI OR Google OR Meta OR "Snap Inc" OR "Perplexity AI" OR Claude OR Gemini) ("training data" OR "AI training" OR dataset) (copyright OR DMCA OR unauthorized)',
    'document_type:"PACER Document" (short_description:complaint OR short_description:"amended complaint" OR short_description:petition) ("shadow library" OR LibGen OR "Library Genesis" OR Z-Library OR Books3 OR piracy OR pirated) ("AI training" OR "training data" OR LLM)',
    'document_type:"PACER Document" (short_description:complaint OR short_description:"amended complaint") (YouTube OR "video dataset" OR scraping OR circumvent OR "technical protection" OR DMCA) ("AI training" OR "training data" OR model)',
    'document_type:"PACER Document" (short_description:complaint OR short_description:"amended complaint") (lyrics OR "music publisher" OR "musical works") ("AI training" OR model OR LLM) (copyright OR unauthorized)',
]

# 뉴스(RSS) 보강 쿼리 (최근 3일)
NEWS_QUERIES = [
    '("AI training" OR "model training" OR LLM) (lawsuit OR sued OR litigation) (copyright OR pirated OR unauthorized OR "shadow library" OR scraping) when:3d',
    '(Anthropic OR OpenAI OR Google OR Meta OR "Snap Inc" OR "Perplexity AI") (lawsuit OR sued) (training data OR dataset OR copyright OR DMCA) when:3d',
    '("DMCA" OR "copyright infringement") ("AI model" OR "AI training" OR "training data") when:3d',
    '("AI data contract" OR "AI 데이터 계약" OR "data licensing agreement") when:3d',
]
