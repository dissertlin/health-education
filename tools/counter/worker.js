/**
 * 衛教詳細版瀏覽次數計數器
 * 部署於使用者自己的 Cloudflare 帳號，資料不經過任何第三方服務。
 *
 * 隱私設計：整支程式只讀寫一個整數。
 * 沒有任何一行寫入 IP、時間戳、User-Agent、Referer 或 cookie，
 * KV 裡存的內容就只有 "views:<頁面代號>" -> "數字"。
 *
 * 路徑：
 *   POST /hit?p=<代號>   計數 +1（限 dissertlin.github.io 呼叫，爬蟲不計）
 *   GET  /stats          十份一覽表（純讀取，不會 +1）
 *   GET  /stats.json     同上，JSON 格式
 */

const ORIGIN = "https://dissertlin.github.io";
const SITE = "https://dissertlin.github.io/health-education";

// 允許計數的頁面代號；不在清單內的一律拒絕，避免有人亂塞 key
const PAGES = {
  "af-intro": "認識心房顫動",
  "af-meds": "心房顫動的用藥指南",
  "af": "心房顫動｜電燒手術",
  "svt": "認識上心室頻脈",
  "brady": "心率過慢",
  "pacemaker": "裝置心臟節律器",
  "bp": "血壓控制",
  "oh": "姿態性低血壓",
  "hf": "認識心臟衰竭",
  "gout": "痛風控制",
};

// 明顯的爬蟲不計數：既避免灌水，也省下 KV 的每日寫入額度
const BOT = /bot|crawler|spider|slurp|crawling|preview|monitor|headless|curl|wget|python-requests|facebookexternalhit|whatsapp|line-poker/i;

async function readAll(env) {
  const slugs = Object.keys(PAGES);
  const nums = await Promise.all(
    slugs.map((s) => env.COUNTER.get("views:" + s))
  );
  return slugs.map((s, i) => ({
    p: s,
    title: PAGES[s],
    n: parseInt(nums[i] || "0", 10) || 0,
  }));
}

function statsPage(rows) {
  const total = rows.reduce((a, r) => a + r.n, 0);
  const sorted = [...rows].sort((a, b) => b.n - a.n);
  const tr = sorted
    .map(
      (r) =>
        `<tr><td><a href="${SITE}/${r.p}/">${r.title}</a></td>` +
        `<td class="n">${r.n.toLocaleString("zh-TW")}</td></tr>`
    )
    .join("");
  return `<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>衛教詳細版瀏覽次數</title><style>
:root{color-scheme:light dark}
body{margin:0;padding:24px 16px 48px;font:16px/1.7 -apple-system,"PingFang TC","Noto Sans TC",sans-serif;background:#f4f9fa;color:#18334d}
@media(prefers-color-scheme:dark){body{background:#0f1720;color:#e8f1f5}}
.w{max-width:560px;margin:0 auto}
h1{font-size:1.25rem;margin:0 0 .2em}
p.sub{margin:.2em 0 1.2em;color:#5b6e80;font-size:.9rem}
table{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden}
@media(prefers-color-scheme:dark){table{background:#161f2a}}
th,td{padding:10px 14px;text-align:left;border-bottom:1px solid #d9e5ea}
@media(prefers-color-scheme:dark){th,td{border-color:#27333f}}
th{background:#eef7f8;font-size:.85rem}
@media(prefers-color-scheme:dark){th{background:#16262a}}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;font-weight:700;white-space:nowrap}
a{color:#15a99d}
tfoot td{font-weight:700;border-bottom:0}
</style></head><body><div class="w">
<h1>衛教詳細版瀏覽次數</h1>
<p class="sub">依次數排序。開啟這一頁<b>不會</b>增加任何計數。</p>
<table><thead><tr><th>頁面</th><th class="n">累計次數</th></tr></thead>
<tbody>${tr}</tbody>
<tfoot><tr><td>十份合計</td><td class="n">${total.toLocaleString("zh-TW")}</td></tr></tfoot>
</table>
<p class="sub" style="margin-top:1.2em">資料只有數字本身，沒有儲存任何 IP、時間或裝置資訊。</p>
</div></body></html>`;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";

    // ---- 統計頁：純讀取，不計數，任何人都可以看（數字本來就顯示在公開頁面上）----
    if (request.method === "GET" && (path === "/stats" || path === "/stats.json")) {
      const rows = await readAll(env);
      if (path === "/stats.json") {
        return new Response(JSON.stringify({ pages: rows }, null, 2), {
          headers: {
            "Content-Type": "application/json; charset=utf-8",
            "Cache-Control": "no-store",
          },
        });
      }
      return new Response(statsPage(rows), {
        headers: {
          "Content-Type": "text/html; charset=utf-8",
          "Cache-Control": "no-store",
        },
      });
    }

    // ---- 計數 ----
    const cors = {
      "Access-Control-Allow-Origin": ORIGIN,
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Max-Age": "86400",
      "Vary": "Origin",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }
    if (request.method !== "POST") {
      return new Response("method not allowed", { status: 405, headers: cors });
    }
    if (request.headers.get("Origin") !== ORIGIN) {
      return new Response("forbidden", { status: 403, headers: cors });
    }

    const page = url.searchParams.get("p") || "";
    if (!Object.prototype.hasOwnProperty.call(PAGES, page)) {
      return new Response("unknown page", { status: 400, headers: cors });
    }

    const key = "views:" + page;
    let n = parseInt((await env.COUNTER.get(key)) || "0", 10);
    if (!Number.isFinite(n) || n < 0) n = 0;

    const ua = request.headers.get("User-Agent") || "";
    if (ua && !BOT.test(ua)) {
      n += 1;
      await env.COUNTER.put(key, String(n));
    }

    return new Response(JSON.stringify({ p: page, n }), {
      status: 200,
      headers: {
        ...cors,
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "no-store",
      },
    });
  },
};
