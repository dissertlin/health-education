/**
 * 衛教詳細版瀏覽次數計數器
 * 部署於使用者自己的 Cloudflare 帳號，資料不經過任何第三方服務。
 *
 * 隱私設計：整支程式只讀寫一個整數。
 * 沒有任何一行寫入 IP、時間戳、User-Agent、Referer 或 cookie，
 * KV 裡存的內容就只有 "views:<頁面代號>" -> "數字"。
 */

const ORIGIN = "https://dissertlin.github.io";

// 允許計數的頁面代號；不在清單內的一律拒絕，避免有人亂塞 key
const PAGES = [
  "af", "af-intro", "af-meds", "bp", "brady",
  "gout", "hf", "oh", "pacemaker", "svt",
];

// 明顯的爬蟲不計數：既避免灌水，也省下 KV 的每日寫入額度
const BOT = /bot|crawler|spider|slurp|crawling|preview|monitor|headless|curl|wget|python-requests|facebookexternalhit|whatsapp|line-poker/i;

export default {
  async fetch(request, env) {
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

    const page = new URL(request.url).searchParams.get("p") || "";
    if (!PAGES.includes(page)) {
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
