# 變更摘要（分支 `claude/improve-health-education`）

原則：**未更動任何醫療／衛教文字、數字、音檔或單張 SVG／PDF。** 有疑慮處只記錄在 [REVIEW-NOTES.md](REVIEW-NOTES.md)。

## 階段一：內容檢查（錯字、語句、連結）

- 新增 `tools/audit_links.py`（站內連結／錨點／資源）與 `tools/audit_text.py`（疊字、標點、簡體字、術語）。
- 檢查 195 個 HTML：發現並修正 **14 個失效連結**：
  - `patient-education-preview/af-meds/faq.html` 的「上一頁」指向不存在的 `topic-6.html` → 改指 `help.html`。
  - `patient-education-preview/brady/topic-1~6.html` 的「回目錄」指向不存在的 `#toc`（13 處）→ 改指同資料夾 `index.html`。
- 外部連結僅 3 種（GitHub Pages 兩個、計數器統計頁），回應皆為 200。
- 文字檢查未發現需要修改的錯字；「心室上頻脈／上心室頻脈」用語並存，已標註於 REVIEW-NOTES（未更動）。
- `.gitignore` 加入 `__pycache__/`，並移除已被提交的 `.pyc`。

## 階段二：頁面結構、導覽、手機版

- 17 個詳細版與首頁：加入 `<main id="main">` 地標與「跳到主要內容」連結。
- 17 個詳細版：頁尾新增「上一個／下一個主題」導覽（順序同首頁卡片）。
- 手機版：目錄在 ≤560px 改單欄、版心左右邊距 16px、圖示卡片單欄；`scroll-margin` 讓錨點跳轉不貼頂。以 Playwright 檢查全部 195 頁在 320／375／390px 寬度皆無橫向溢出（`tools/audit_mobile.js`）。
- 語音版 `af-meds`、`brady`、總覽頁與兩個示範頁：補上 skip link／`main#main`。

## 階段三：無障礙與載入效能

- 無障礙：所有頁面有 `lang`、`title`、viewport；新增鍵盤焦點樣式（`:focus-visible`）、`prefers-reduced-motion` 時關閉平滑捲動；裝飾性 inline SVG（約 130 個）加 `aria-hidden="true" focusable="false"`；語音版總覽補 meta description。
- 效能：
  - 語音版醫師頭像 19 份由 1254×1254（1.5 MB）縮為 320×320（約 120 KB）：repo 由約 206 MB 降至約 181 MB，語音版每個主題頁首次載入少傳約 1.4 MB。
  - 單張預覽圖與首頁縮圖加 `width`/`height`（避免版面位移）、`loading="lazy"`、`decoding="async"`。
  - 補上 170 頁缺少的 favicon／apple-touch-icon。
- 新增 `tools/audit_a11y.py`（lang／main／skip link／alt／尺寸／svg 等靜態檢查）。

## 階段四：文件與維護指引

- 新增 [MAINTENANCE.md](MAINTENANCE.md)：目錄結構、不可更名的網址、檢查腳本用法、新增主題清單、內容查核週期、圖片準則。
- 新增 [REVIEW-NOTES.md](REVIEW-NOTES.md)：待人工確認事項（術語、重複示範頁、未引用檔案、PDF 重複、標題層級、查核日期格式等）。
- 更新 `README.md`：補上遺漏的「認識心肌梗塞」「抗凝血藥與抗血小板藥」兩列、語音版與維護文件連結。
- 更新 `tools/counter/README.md`（「十份」→ 17 份）；`patient-education-preview/README-交接說明.md` 加註已過時說明。

## 驗證方式與限制

- `tools/audit_links.py`：站內問題 0。`tools/audit_mobile.js`：320／375／390px 溢出 0。
- `tools/audit_a11y.py` 剩餘項目皆為刻意保留（首屏頭像不 lazy、h2→h4 跳級，見 REVIEW-NOTES）。
- 未做螢幕閱讀器實測、未重新試聽音檔、未做醫療內容審閱。
