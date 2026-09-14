# 病人衛教資訊圖表

心臟科 A5 病人衛教資訊圖表（繁體中文），向量檔可無損放大、附列印用 PDF。

**線上版：** https://dissertlin.github.io/health-education/

| 單張 | 網址 | 檔案 |
| --- | --- | --- |
| 心房顫動｜心律不整電燒手術 | `/af/` | `af/af-ablation.svg` · `af/af-ablation.pdf` · `af/index.html`（詳細版長文，含台灣健保與自費費用）|
| 心率過慢｜安心觀察指南 | `/brady/` | `brady/bradycardia.svg` · `brady/bradycardia.pdf` · `brady/index.html`（詳細版長文）|
| 認識心房顫動 | `/af-intro/` | `af-intro/af-basics.svg` · `af-intro/af-basics.pdf` · `af-intro/index.html`（詳細版長文）|
| 心房顫動的用藥指南 | `/af-meds/` | `af-meds/af-meds.svg` · `af-meds/af-meds.pdf` · `af-meds/index.html`（詳細版長文）|
| 血壓控制 | `/bp/` | `bp/bp.svg` · `bp/bp.pdf` · `bp/index.html`（詳細版長文）|
| 姿態性低血壓 | `/oh/` | `oh/oh.svg` · `oh/oh.pdf` · `oh/index.html`（詳細版長文）|
| 痛風控制 | `/gout/` | `gout/gout.svg` · `gout/gout.pdf` · `gout/index.html`（詳細版長文）|
| 裝置心臟節律器 | `/pacemaker/` | `pacemaker/pacemaker.svg` · `pacemaker/pacemaker.pdf` · `pacemaker/index.html`（詳細版長文）|
| 認識心臟衰竭 | `/hf/` | `hf/hf.svg` · `hf/hf.pdf` · `hf/index.html`（詳細版長文）|

每張單張右上角的 QR code 指向該張自己的頁面（不是首頁），病人掃描即可在手機上看電子版。

> 注意命名：`/af/` 是**電燒手術**那張，`/af-intro/` 是**認識心房顫動**那張。`/af/` 的網址已燒進單張的 QR，不要更名。

`/af-intro/` 除了單張本身，另有一份依單張各重點展開的**網路詳細版長文**（12 個章節，含 CHA₂DS₂-VA、亞洲人 NOAC 建議、自我測脈搏、常見問題）。

## 新增一張衛教單

1. 建立 `<slug>/` 資料夾，放入 `<name>.svg`
2. 嵌入 QR code（需 `pip install segno`）：

```bash
python3 tools/add_qr.py <slug>/<name>.svg <slug>/<name>.svg \
  "https://dissertlin.github.io/health-education/<slug>/" \
  --x 463 --y 14 --caption-pos below --caption-fill "#46637f" --panel-stroke "#bcdfe3"
```

深色頁首的單張改用 `--caption-pos left --caption-fill "#d8fbff" --panel-stroke none`。
腳本可重複執行，會自動覆蓋舊的 QR。

3. 產生 A5 PDF、複製一份 `index.html` 改標題，並在首頁 `index.html` 加一張卡片。

## 版權與授權

© 2026 林祐賸醫師　保留所有權利。

**醫療專業人員可以直接列印給自己的病人使用**，也可以分享網頁版的連結；但**重製、散布檔案、改作或商業使用需事先取得同意**。

完整條款見 [LICENSE](LICENSE)。

## 免責

本資訊供醫病共同決策參考，**不取代個別診療**，亦不提供任何藥物劑量建議。
內容依編製當時的臨床指引整理，各單張與詳細版頁尾均列出資料來源與查核日期。
