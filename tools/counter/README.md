# 瀏覽次數計數器（自建，不經第三方）

十份衛教詳細版**各自獨立計數**，資料存在您自己的 Cloudflare 帳號裡。

## 隱私設計

`worker.js` 整支程式只讀寫一個整數。沒有任何一行寫入 IP、時間、
User-Agent、Referer 或 cookie —— 資料庫裡就只有這十筆：

```
views:af         -> 123
views:af-intro   -> 456
...
views:svt        -> 78
```

Cloudflare 作為您的服務供應商，在傳輸過程中技術上會經手 IP，
這點無法避免（GitHub 現在送出網頁時也一樣）。差別在於**不會被存進計數資料**，
也不會交給任何與您無關的公司。

## 設定步驟（約 10 分鐘，只需做一次）

Cloudflare 後台的選單名稱偶爾會調整，若字樣略有不同請找相近的位置。

1. **註冊免費帳號** —— <https://dash.cloudflare.com/sign-up>，不需要有網域、不需要信用卡。

2. **建立 KV 儲存空間**
   左側選單 → `Storage & Databases` → `KV` → `Create a namespace`
   名稱填 `health-education-counter` → 建立。

3. **建立 Worker**
   左側選單 → `Compute (Workers)` → `Create` → `Start with Hello World!` → `Deploy`
   名稱建議 `he-counter`。

4. **貼上程式碼**
   進入剛建立的 Worker → `Edit code` → 把編輯器內容全部刪掉，
   貼上本資料夾的 `worker.js` 全文 → 右上角 `Deploy`。

5. **綁定 KV**（這一步沒做，計數會失敗）
   Worker → `Settings` → `Bindings` → `Add` → `KV namespace`
   - Variable name 一定要填：**`COUNTER`**（大寫，不能改）
   - KV namespace 選：`health-education-counter`
   → `Deploy`

6. **複製 Worker 網址**
   在 Worker 頁面上方，形如 `https://he-counter.你的帳號.workers.dev`
   把這個網址給 Claude，或自己執行下一步。

## 裝到十份頁面

```bash
python3 tools/counter/add_counter.py https://he-counter.你的帳號.workers.dev
```

## 從哪裡看數字

用瀏覽器直接開（純讀取，**不會**增加計數，可加書籤）：

- `https://he-counter.dissertlin.workers.dev/stats` —— 十份一覽表，依次數排序，含合計
- `https://he-counter.dissertlin.workers.dev/stats.json` —— 同樣內容的 JSON

也可以在 Cloudflare 後台 `Storage & Databases` → `KV` → namespace 直接看 `views:*` 十筆。
注意：**自己去看衛教頁面本身會讓數字 +1**，日常查看請用上面的 /stats。

## 歸零

```bash
npx wrangler login                                   # 您自己授權一次
bash tools/counter/reset.sh <KV_NAMESPACE_ID>        # 十份全部歸零
bash tools/counter/reset.sh <KV_NAMESPACE_ID> svt bp # 或只歸零指定幾份
```

或在後台 KV 頁面把 `views:xxx` 的值直接改成 `0`。

## 拿掉

```bash
python3 tools/counter/add_counter.py --remove
```

插入的內容都以 `<!-- 瀏覽次數 begin/end -->` 與 `/* 瀏覽次數 begin/end */`
包住，移除後與原檔逐位元相同，不留任何痕跡。

## 已知限制（請先知道）

- **算的是人次不是人數。** 同一個人重新整理三次就是三次。
- **KV 免費額度每天 1,000 次寫入。** 也就是全站每天約 1,000 次瀏覽。
  超過之後當天數字會停止增加（頁面仍正常顯示，不會壞掉），隔天自動恢復。
  程式已過濾常見爬蟲，避免無謂消耗。
- **同時多人進入可能少算。** KV 沒有原子加法，程式是「讀出來 +1 再寫回」，
  兩個人同一瞬間進來可能只加到 1。以這個網站的流量幾乎不會發生；
  若日後真的在意精確度，可改用 Durable Objects。
- **計數失敗時不顯示。** Worker 沒回應、被瀏覽器擴充套件擋掉、
  或讀者關閉 JavaScript 時，那一行會自動隱藏，不會出現壞掉的畫面。
- **舊瀏覽器不計數。** 使用 `fetch`，非常舊的瀏覽器會直接略過。
