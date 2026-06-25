#!/usr/bin/env bash
#
# 대시보드 실행 런처.
#
# docker-compose 는 /etc/environment 를 직접 읽지 않는다. compose 가 ${GEMINI_API_KEY}
# 를 채우는 소스는 (1) 실행 셸의 환경변수, (2) .env 파일 뿐이다.
# 이 스크립트는 셸에 GEMINI_API_KEY 가 없으면 /etc/environment 에서 꺼내 export 한 뒤
# docker-compose 를 띄운다. 그래서 다음처럼 키를 앞에 붙이지 않아도 Gemini 기능이 동작한다:
#
#   ./scripts/up.sh                  # /etc/environment 의 GEMINI_API_KEY 자동 사용
#   GEMINI_API_KEY=xxx ./scripts/up.sh   # 명시적으로 줘도 됨(이게 우선)
#   ./scripts/up.sh --build          # 추가 인자는 docker-compose 로 그대로 전달
#
set -euo pipefail

# 스크립트 위치(scripts/) 기준으로 dashboard 루트로 이동 → 기존 명령과 동일한 경로 해석 보장
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DASHBOARD_DIR="$(dirname "$SCRIPT_DIR")"
cd "$DASHBOARD_DIR"

# GEMINI_API_KEY 확보: 이미 export 돼 있으면 그대로, 없으면 /etc/environment 에서 추출
if [ -z "${GEMINI_API_KEY:-}" ] && [ -r /etc/environment ]; then
    line="$(grep -E '^[[:space:]]*GEMINI_API_KEY=' /etc/environment | tail -n1 || true)"
    if [ -n "$line" ]; then
        val="${line#*=}"
        val="${val%\"}"; val="${val#\"}"   # 양끝 큰따옴표 제거
        val="${val%\'}"; val="${val#\'}"   # 양끝 작은따옴표 제거
        export GEMINI_API_KEY="$val"
    fi
fi

if [ -z "${GEMINI_API_KEY:-}" ]; then
    echo "⚠️  GEMINI_API_KEY 를 찾지 못했습니다(/etc/environment·셸 모두 없음). Gemini 기능(월간 보고서 등)이 비활성화됩니다." >&2
else
    echo "✅ GEMINI_API_KEY 로드됨 — Gemini 기능 활성화"
fi

# docker-compose(구형) / docker compose(플러그인) 자동 선택
if command -v docker-compose >/dev/null 2>&1; then
    exec docker-compose -f docker/docker-compose.yml up -d "$@"
else
    exec docker compose -f docker/docker-compose.yml up -d "$@"
fi
