# 待人工確認事項

本檔只**標註**疑慮，沒有改動任何醫療或衛教內容。是否調整，請由作者／醫療審閱者決定。

## A. 內容與用語

1. **術語不一致：「心室上頻脈」與「上心室頻脈」並用。** 全站「心室上頻脈」約 62 處（首頁卡片、`svt/`、`ep/`、語音版、`tools/counter/worker.js` 標籤），「上心室頻脈」約 40 處。臨床中 supraventricular tachycardia 兩種譯法都有人用，請作者決定統一用哪一個（統一需同步修改語音版逐字稿與 MP3）。
2. **文字檢查的範圍與限制。** `tools/audit_text.py` 只做形式檢查（疊字、標點、簡體字、常見誤字），結果除上述術語外沒有發現需修改的錯字；它**無法判斷醫學正確性**。本次未做醫療內容審閱，各頁數字（LDL／HbA1c 目標、血壓 722、劑量相關敘述、費用等）請依「資料來源」逐頁覆核。
3. **查核日期。** 各頁頁尾標示「查核至 2026-09／2026 年 9 月／2026 年 10 月」，格式不統一；建議統一為同一格式。
4. **標點風格。** `patient-education-preview/af/topic-3.html` 的「BMI＝體重(公斤)÷身高(公尺)²」使用半形括號，與全站全形括號慣例不同；僅屬排版，未更動。
5. **`svt/index.html`「怦怦怦」** 為擬聲詞，屬正常用法，非錯字。

## B. 結構與檔案

1. **重複示範頁。** `af-meds-cute-d/` 與 `af-meds-full-content-demo/` 內容逐檔相同（各約 8.8 MB）、首頁未連結，且與 `patient-education-preview/af-meds/` 重複。若確認無外部連結指向，建議刪除其一或兩者（未動，因 GitHub Pages 網址可能已被分享）。
2. **未被引用的檔案。** `assets/logo-badge-1254.png`（1.1 MB）、`assets/doctor.png`、`assets/logo-lockup.svg`、`assets/logo-mark.svg`、`assets/logo.svg`、`patient-education-preview/assets/topic-art-new.png` 目前沒有任何頁面或腳本引用，可能是原稿備份，未刪。
3. **PDF 重複。** 各主題的 PDF 在 `<slug>/` 與 `patient-education-preview/<slug>/handout.pdf` 各存一份（`gout` 各約 2 MB）。語音版可考慮改連根目錄的 PDF 以省空間，但需確認離線使用需求。
4. **標題層級跳級。** `af-meds/index.html`、`lipid/index.html`、`af-meds-*/two-meds.html`、`patient-education-preview/af-meds/two-meds.html` 有 h2→h4（為了沿用 h4 的視覺樣式）。對輔助科技有些許影響，改成 h3 會改變外觀，需連同 CSS 調整。
5. **語音版與詳細版同步。** 語音版內文為詳細版的節錄／改寫，之後詳細版有修改時不會自動同步（見 MAINTENANCE.md 第 4 節）。
6. **`patient-education-preview/README-交接說明.md`** 為早期十大主題的交接紀錄（已加註更新說明），內容未重寫。
7. **瀏覽計數器** 依賴作者的 Cloudflare Worker（`he-counter.dissertlin.workers.dev`，目前回應正常）；失敗時頁面會靜默不顯示，不影響閱讀。首頁的「各篇衛教瀏覽次數統計」連結公開可見，請確認這是預期行為。
8. **首屏醫師頭像** 仍約 120 KB，且語音版每個主題各存一份相同檔案；若要再瘦身可改為共用 `patient-education-preview/assets/` 內一份，但需改動所有頁面路徑。
