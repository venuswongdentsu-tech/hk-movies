#!/usr/bin/env bash
# 一鍵部署到 GitHub Pages。需要先行建立 ~/.hermes/github_token（600 權限）內含 PAT。
set -euo pipefail
USER="venuswongdentsu-tech"
REPO="hk-movies"
API="https://api.github.com"
REPO_DIR="/workspace/hk-movies-app"
TOKF="$HOME/.hermes/github_token"

[ -f "$TOKF" ] || { echo "缺 $TOKF"; exit 1; }
TOKEN="$(tr -d ' \n\r' < "$TOKF")"
[ -n "$TOKEN" ] || { echo "token 空"; exit 1; }

echo "== 驗證 token =="
curl -s -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json" "$API/user" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print('登入為:',d.get('login') or d)"

echo "== 建立 repo（已存在則忽略）=="
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json" \
  "$API/user/repos" \
  -d "{\"name\":\"$REPO\",\"description\":\"香港電影週報 PWA\",\"public\":true,\"has_issues\":false,\"has_wiki\":false}" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('full_name') or d.get('message'))"

echo "== 設定 git remote / 憑證 =="
git -C "$REPO_DIR" config credential.helper "store --file=$HOME/.git-credentials"
umask 077; printf 'https://x-access-token:%s@github.com\n' "$TOKEN" > "$HOME/.git-credentials"
git -C "$REPO_DIR" remote remove origin 2>/dev/null || true
git -C "$REPO_DIR" remote add origin "https://github.com/$USER/$REPO.git"
git -C "$REPO_DIR" branch -M main

echo "== push =="
git -C "$REPO_DIR" push -u origin main

echo "== 開啟 GitHub Pages =="
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json" \
  "$API/repos/$USER/$REPO/pages" \
  -d '{"source":{"branch":"main","path":"/"}}' \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('html_url') or d.get('message'))"

URL="https://$USER.github.io/$REPO/"
echo "== 等待 Pages 生效（最多 180 秒）=="
for i in $(seq 1 36); do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$URL" || echo 000)
  echo "  [$i] $code  $URL"
  [ "$code" = "200" ] && break
  sleep 5
done
echo "完成：$URL"
