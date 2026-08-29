# 病人衛教資訊圖表

心房顫動電燒手術的 A5 病人衛教資訊圖表（繁體中文）。

**線上版：** https://dissertlin.github.io/health-education/

| 檔案 | 說明 |
| --- | --- |
| `af-ablation.svg` | 原始向量圖，A5（148 × 210 mm），可無損放大 |
| `af-ablation.pdf` | A5 列印用 PDF |
| `index.html` | GitHub Pages 首頁 |

單張右上角的 QR code 指向本站，病人掃描即可在手機上看電子版。

## 授權與免責

本資訊供醫病共同決策參考，不取代個別診療。資料來源查核至 2026-08，詳見圖表底部。

## 重新產生 QR code

若網址改變，重跑一次即可（需 `pip install segno`）：

```bash
python3 tools/add_qr.py af-ablation.svg af-ablation.svg "https://新網址/" "掃描看電子版"
```

腳本可重複執行，會自動覆蓋舊的 QR。
