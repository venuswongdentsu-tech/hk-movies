# 香港電影週報（HK Movie Weekly）— PWA

香港戲院每週電影報告的手機 App（Progressive Web App）：新上映、仍在上映、中英對照片名、海報、主演、多平台評分，以及整合自香港觀眾影評的 👍正評／👎負評。

## 加到 iPhone 主畫面
1. iPhone 用 **Safari** 打開下面網址
2. 撳底部 **分享** 圖示 → **加至主畫面**
3. 之後就可似一般 App 咁開，冇網絡都睇得到（顯示上次更新嘅資料）

> 網址：`https://<你的 GitHub 用戶名>.github.io/hk-movies/`

## 功能
- 分區瀏覽：本週新上映 / 仍然上映
- 搜尋片名（中／英）、依評分或戲院數排序
- 點卡片睇詳情：劇情、導演、主演（頭 5 位）、各平台評分、正／負評整合
- 離線可用（service worker 快取）、可加到主畫面（standalone）

## 資料來源
wmoov（上映日期、戲院數、人氣、評分）· HKMovie6（評分、讚好、影評）· IMDb · Rotten Tomatoes · Google

**限制：** Google 電影用戶評分無公開可抓取端點，一律顯示「—」；部分港產／亞洲片在 Rotten Tomatoes 無獨立頁面，同樣顯示「—」（不代表套戲差）。

## 收錄範圍

`scrape_wmoov.py` 每次由 wmoov「現正上映」列表**自動發現全部電影 ID**（唔再靠人手維護清單），再逐套抓詳情頁；`build_shortlist.py` 收錄**所有至少 1 間戲院有場次**嘅電影（包括經典重映、1 院上映），因此片單會隨每週實際上畫情況增減（2026-11 約 96 套）。

## 更新流程（每週）
```
bash /workspace/movies/weekly_pipeline.sh               # 全流程（清快取→抓→整合）
bash /workspace/movies/weekly_fetch.sh                 # = 上面 + 影評摘要 + 建站推送
# → 之後由 agent 讀 reviews_digest.txt、更新 sentiment.json（每次最多 60 套，優先未處理嘅戲）
bash /workspace/hk-movies-app/refresh_and_push.sh      # 建站並推送
```

Site 完全靜態，`git push` 後 GitHub Pages 約 1 分鐘內自動更新。

## 檔案
- `index.html` — App 外殼（UI + 互動邏輯）
- `data.js` — 每週更新的電影資料（由 `build_site.py` 產生）
- `posters/` — 海報（300×450）
- `icons/` — App 圖示
- `manifest.webmanifest` — PWA manifest
- `sw.js` — service worker（離線快取）
- `build_site.py` — 由 `/workspace/movies` 的資料產生整個站
