#!/usr/bin/env bash
# 每週更新：重建網站資料並推到 GitHub Pages
# 用法：bash hourly_refresh.sh   （實際每週由 cron 執行）
set -euo pipefail
REPO="/workspace/hk-movies-app"
MV="/workspace/movies"

echo "== 1/3 重建站台資料 =="
cd "$REPO" && python3 build_site.py

echo "== 2/3 commit =="
cd "$REPO"
git add -A
if git diff --cached --quiet; then
  echo "冇改動，跳過 push。"; exit 0
fi
git commit -q -m "weekly update $(TZ=Asia/Hong_Kong date +%Y-%m-%d)"

echo "== 3/3 push =="
git push -q origin main
echo "完成。GitHub Pages 約 1 分鐘內更新。"
