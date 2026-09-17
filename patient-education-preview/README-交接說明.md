# 十大衛教主題・語音完整版

完整解壓縮後，開啟最外層 index.html。共有 10 個主題、71 個 HTML、75 個固定 MP3（約 81.0 分鐘）、10 份 PDF。
這是獨立 GitHub 預覽版，供審閱及後續整合；既有網站與 QR code 網址保留。

## 主題

1. af-intro：認識心房顫動
2. bp：血壓控制
3. brady：心率過慢（既有 brady-cute-d 完整成品）
4. gout：痛風控制
5. hf：心臟衰竭
6. oh：姿態性低血壓
7. pacemaker：心臟節律器
8. svt：上心室頻脈
9. af：心房顫動電燒
10. af-meds：心房顫動用藥指南（使用者提供的完整範例 ZIP）

## Claude 整合注意事項

- 建議在 GitHub 的 patient-education-voice/ 下面整合；本包 brady、af-meds 等名稱僅在新總資料夾內使用，不能覆蓋 repository 根目錄的舊同名資料夾。
- 使用整份資料夾，保留 HTML、assets、audio、handout.pdf。每個主題首頁都有「回十大主題總覽」。
- 用藥指南的 PDF 下載已改為包內 handout.pdf，其他圖片和音檔也全部在包內，不依赖原 GitHub 網站才能播放。
- 用藥指南 12 段與心率過慢 7 段沿用原始 MP3，逐位元核對相同；只調整本機首頁導覽及用藥指南 PDF 路徑，未重寫這兩份醫療內容。
- 其餘八份共 56 段，由本次八份 PDF 原文製作。使用台灣女聲 zh-TW-HsiaoChenNeural、速度 -25%；舊 D 聲線的精確原始參數未能核實，不能保證新舊速度完全相同。
- 新八份附 transcripts/、source-content.json、SRT；原兩份沒有另行推測或重建逐字稿。
- 原始 PDF 保留；不要更動已印製 QR code 所指的既有網址。整合版面時不要自行修改醫療文字、數字或音檔。
- 保留用藥指南與心率過慢原網站，發布前確認新總首頁的十張卡片及全部音訊連結。

## 核對紀錄

新八份的原文與音檔核對見 eight-topic-verification-report.json。
本整合包所有相對連結均已檢查，兩份匯入網站在 320、390、768、1440 像素寬度檢查，19 個匯入音檔經瀏覽器解碼，兩份網站播放、暫停、繼續及重播均測試通過。
驗證不代表逐段人工試聽或重新醫療審定。

## 首頁圖示更新
十張卡片已套用核准的可愛醫療插畫。圖像集中在 assets/topic-illustrations.png，由 assets/topic-icons.css 定位顯示；整合時請保留兩個檔案。標題仍為 HTML 文字。衛教內容、音檔與各主題內頁沒有變更。
