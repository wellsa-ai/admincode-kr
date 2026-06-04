#!/bin/bash
# admincode-kr 분기 갱신 (1/4/7/10월 1일 12:00 KST) — 법정동은 행정구역 개편 시만 변경
# cron: 0 12 1 1,4,7,10 * /Users/sammy/workspaces/lawdata-wellsa/admincode-kr/pipeline/cron_update.sh

set -e

cd /Users/sammy/workspaces/lawdata-wellsa/admincode-kr
LOG="/Users/sammy/workspaces/lawdata-wellsa/admincode-kr/logs/update.log"
mkdir -p "$(dirname "$LOG")"

echo "=== $(date) ===" >> "$LOG"

# code.go.kr 전체자료 다운로드 → md + json 재빌드
python3 pipeline/build.py >> "$LOG" 2>&1

# 변경 있으면 커밋 + push (행정구역 개편 발생)
git add -A
if git diff --cached --quiet; then
    echo "no changes (행정구역 개편 없음)" >> "$LOG"
else
    git commit -m "chore: 법정동 데이터 분기 갱신 ($(date +%Y-%m-%d))" >> "$LOG" 2>&1
    git push origin main >> "$LOG" 2>&1
    echo "pushed" >> "$LOG"

    # 미니 보고 + obs-chatbot 동기화 알림
    ~/bin/mini-ask -t "[admincode-kr] 법정동 데이터 변경 감지(행정구역 개편) → GitHub 푸시 완료. obs-chatbot legal_dong.json 동기화 필요: curl -sL https://raw.githubusercontent.com/wellsa-ai/admincode-kr/main/data/legal_dong.json -o backend/data/legal_dong.json 후 배포" >> /dev/null 2>&1 || true
fi
