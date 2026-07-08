#!/usr/bin/env bash
#
# 운영 서버용 정본 CSV 자동 반영 스크립트.
#
# analyzer PR 이 merge 되면 GitHub main 만 갱신된다. 대시보드 backend 는
# 요청 시마다 디스크의 data/*.csv 를 직접 읽으므로(재시작 불필요),
# 운영 서버 호스트에서 이 스크립트로 git pull 만 해주면 새 CSV 가 반영된다.
# (운영 서버는 사설망이라 GitHub webhook 이 닿지 않음 → cron 폴링 방식)
#
# 설치 (운영 서버 192.168.10.2 에서 1회):
#   (crontab -l 2>/dev/null; echo "*/5 * * * * <repo>/dashboard/scripts/auto_pull.sh") | crontab -
#
# 로그: ~/.cache/ai-suit-sensing/auto_pull.log
set -u

REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
LOG_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/ai-suit-sensing"
LOG="${LOG_DIR}/auto_pull.log"
LOCK="${LOG_DIR}/auto_pull.lock"
mkdir -p "$LOG_DIR"

log() { echo "$(date '+%F %T') $*" >> "$LOG"; }

# 동시 실행 방지 (이전 회차가 네트워크 지연으로 남아있을 수 있음)
exec 9>"$LOCK"
flock -n 9 || exit 0

cd "$REPO_DIR" || { log "ERROR: repo 없음: $REPO_DIR"; exit 1; }

# 수동 작업 보호: main 브랜치가 아니거나 작업트리가 더럽혀져 있으면 건드리지 않는다
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "main" ]; then
    log "skip: 현재 브랜치가 main 이 아님 ($BRANCH)"
    exit 0
fi
if ! git diff --quiet || ! git diff --cached --quiet; then
    log "skip: 작업트리에 수동 변경사항 있음"
    exit 0
fi

# fetch (프록시가 간헐적으로 끊기면 프록시 우회로 재시도)
if ! git fetch origin main --quiet 2>>"$LOG"; then
    git -c http.proxy= -c https.proxy= fetch origin main --quiet >>"$LOG" 2>&1 \
        || { log "ERROR: fetch 실패(프록시 우회 포함)"; exit 1; }
fi

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
[ "$LOCAL" = "$REMOTE" ] && exit 0  # 변경 없음 → 조용히 종료

if git merge --ff-only origin/main >>"$LOG" 2>&1; then
    log "pulled: ${LOCAL:0:7} -> ${REMOTE:0:7}"
else
    log "ERROR: fast-forward 불가 (로컬 커밋과 분기됨) — 수동 확인 필요"
    exit 1
fi
