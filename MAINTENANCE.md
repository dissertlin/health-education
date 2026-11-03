# 維護指南

站台為純靜態網頁（GitHub Pages，無建置步驟）。**內容原則：未經作者（林祐賸醫師）確認，不改動任何醫療／衛教文字、數字與音檔。**

## 1. 目錄結構

| 路徑 | 內容 |
| --- | --- |
| `index.html` | 首頁：17 張主題卡片、語音版入口 |
| `<slug>/index.html` | 各主題「詳細版」長文（17 個）；同資料夾有 `<name>.svg`（A5 單張）與 `<name>.pdf`（列印用） |
| `patient-education-preview/` | **語音版**：`<slug>/` 內含 `index.html`、`topic-N.html`、`faq.html`、`audio/*.mp3`、`transcripts/`、`handout.pdf`、`assets/` |
| `assets/` | 站台標誌（`logo-badge.png` 為首頁使用） |
| `favicon-*.png`、`apple-touch-icon.png` | 全站圖示 |
| `tools/` | 維護用腳本（見下） |
| `af-meds-cute-d/`、`af-meds-full-content-demo/` | 早期示範頁，彼此內容相同、首頁未連結（見 REVIEW-NOTES.md） |

**不可更名的網址**：每張單張右上角已印有指向 `/<slug>/` 的 QR code。尤其 `/af/` = 電燒手術、`/af-intro/` = 認識心房顫動，請勿對調或更名。

## 2. 自動檢查（修改後、推送前請執行）

```bash
python3 tools/audit_links.py            # 站內連結、錨點、資源是否存在（應為 0 個問題）
python3 tools/audit_links.py --external # 另列出外部連結
python3 tools/audit_a11y.py             # lang / title / main / skip link / alt / 圖片尺寸 / svg 等
python3 tools/audit_text.py             # 文字啟發式檢查：疊字、標點、簡體字、術語（只列出，需人工判斷）
NODE_PATH=$(npm root -g) node tools/audit_mobile.js 320,375,390   # 手機寬度是否橫向溢出（需 Playwright）
```

`audit_a11y.py` 目前仍會列出的項目屬已知且刻意保留：語音版首屏醫師頭像不做 lazy（避免延遲首屏）；少數 h2→h4 標題層級跳級（為了沿用 h4 外觀，更動會改變版面，見 REVIEW-NOTES.md）。

## 3. 新增一個主題的清單

1. 建 `<slug>/`，放入 `<name>.svg`，用 `tools/add_qr.py` 嵌入 QR（指令見 README），輸出 `<name>.pdf`（A5）。
2. 複製既有主題的 `index.html` 當模板（保留 `main#main`、skip link、`.topicnav`、頁尾版權與免責、瀏覽計數區塊），改標題、描述、內容、資料來源與**查核日期**。
3. `<img>` 單張預覽請帶 `width="559" height="794" loading="lazy" decoding="async"`。
4. 首頁 `index.html` 加卡片（`<img>` 同上屬性）；卡片順序即「上一個／下一個主題」順序，需同步調整相鄰頁面的 `.topicnav`。
5. 計數器：頁尾腳本 `P="<slug>"`，並在 `tools/counter/worker.js` 的 `PAGES` 加入同一代號後重新部署（見 `tools/counter/README.md`）。
6. 語音版：在 `tools/voice_scripts/<slug>.py` 寫逐字稿，執行 `python3 tools/voice_gen.py <slug>`，再以 TTS 產生 `audio/*.mp3`（`tools/voice_tts.py`、`tools/voice_install.py`），並把語音版加入 `patient-education-preview/index.html`。
7. 更新 README 的主題表，執行第 2 節的檢查。

## 4. 內容維護週期

- 每個詳細版頁尾標有「資料來源」與「查核至 YYYY 年 M 月」。目前最早為 2026-09；建議**每 6–12 個月**或重大指引更新（ESC／AHA／ADA／台灣各學會）時逐頁重新查核，並更新日期。
- 與費用、健保給付有關的內容（例如電燒手術）變動較快，請優先複查。
- 修改文字後，**語音版的逐字稿與 MP3 不會自動更新**，需同步重做，否則與詳細版不一致。

## 5. 圖片與效能準則

- 單張 SVG 為向量，直接嵌入頁面；不要改成大張 PNG。
- 新增點陣圖請先縮到實際顯示尺寸的 2–3 倍：醫師頭像目前 320×320（顯示 64–96px）。
- 首屏以外的圖片加 `loading="lazy"`，所有 `<img>` 帶 `width`/`height` 以避免版面位移。
- 無障礙：每頁一個 `<h1>`、一個 `<main id="main">`；純裝飾 SVG 加 `aria-hidden="true"`；有意義的 SVG 用 `role="img"` + `aria-label`；連結文字要能獨立理解。

## 6. 版權與免責

見 `LICENSE`。每頁頁尾須保留版權與「不取代個別診療」聲明。
