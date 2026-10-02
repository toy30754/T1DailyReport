# T1DailyReport

每日交易研究部落格：https://uysa247.icu/

- `index.html`：文章列表，依報告日期由新到舊排列；不可用單篇報告覆蓋。
- `reports/YYYY-MM-DD.html`：每篇完整報告的永久網址。
- `templates/index.html`：首頁版型。
- `scripts/build_index.py`：掃描所有報告的 title 與 description，重建靜態首頁。
- Production branch：`main`；Cloudflare Pages 沿用現有靜態部署，不必更改 build 設定。

## 手動發布流程

1. 依使用者指示重新研究，產生完整 HTML，填寫 `<title>` 與 `<meta name="description">`。
2. 新增 `reports/YYYY-MM-DD.html`（Asia/Taipei 報告日期）。同日檔案已存在時保留原文，新篇用 `reports/YYYY-MM-DD-HHMMSS.html`，時間使用 Asia/Taipei。只在使用者明確要求修訂時更新原篇。
3. 報告頁加入 `<a href="/">← 返回文章列表</a>`。
4. 執行 `python3 scripts/build_index.py`，重建首頁。沒有 Python 環境時，依相同規則從完整 reports 目錄重建列表、文章數及月份歸檔；不得漏掉舊文章。
5. 將新報告與更新後的首頁在同一個 commit 提交到 `main`，訊息：`Daily trading report YYYY-MM-DD`。保留 repo 其他檔案。
6. 確認 GitHub 提交成功，並分別核實 Cloudflare 是否已部署。未驗證正式網站時，不宣稱網站部署完成。

首頁使用靜態 HTML，不依賴 GitHub API、JavaScript 或第三方服務載入列表；JavaScript 僅用於搜尋。日期採 ISO 格式排序，同日報告依檔名的時間由新到舊排列。

只在使用者呼叫時執行報告。固定排程保持停用。
