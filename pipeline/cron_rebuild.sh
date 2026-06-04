#!/bin/bash
# admincode-kr 주간 빌드 (매주 일요일 03:00 KST)
# cron: 0 3 * * 0 /Users/sammy/workspaces/lawdata-wellsa/admincode-kr/pipeline/cron_rebuild.sh

set -e

cd /Users/sammy/workspaces/lawdata-wellsa/admincode-kr
LOG="/Users/sammy/workspaces/lawdata-wellsa/admincode-kr/logs/rebuild.log"
mkdir -p "$(dirname "$LOG")"

echo "=== $(date) ===" >> "$LOG"

# 행정표준코드 다운로드 + kr/ md + data/ json 재빌드
python3 pipeline/build.py >> "$LOG" 2>&1 || true

# 변경 있으면 commit + push
git add kr/ data/ README.md >> "$LOG" 2>&1 || true
if ! git diff --cached --quiet; then
    git commit -m "data: 행정표준코드 주간 갱신 ($(date +%Y-%m-%d))" >> "$LOG" 2>&1
    AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
    if [ "$AHEAD" -gt 0 ]; then
        git push origin main >> "$LOG" 2>&1
        echo "pushed $AHEAD commits" >> "$LOG"
        ~/bin/mini-ask -t "[admincode-kr] 행정구역 갱신 $AHEAD건 → GitHub 푸시" >/dev/null 2>&1 || true
    fi
else
    echo "no changes" >> "$LOG"
fi
