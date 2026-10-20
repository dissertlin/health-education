# -*- coding: utf-8 -*-
"""從詳細版抽出常見問題，產生語音版的互動問答頁 faq.html。

知識庫只來自該主題的詳細版（<h2 id="sN">常見問題</h2> 底下的 h3 問答，
以及其餘各節的標題與重點），比對不到就回覆固定的「請洽主治醫師」訊息。
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREV = os.path.join(ROOT, "patient-education-preview")
STOP = set("的了是在有和與及或我你您他它這那些什麼怎麼可以不會要能嗎呢吧啊喔哦為什麼如何請問一個")
STOP_NG = {"可以","什麼","怎麼","要怎","如何","請問","我的","會不","不會","需要","應該","是不","有沒",
           "沒有","哪些","多少","一下","的話","時候","可不","比較","這個","那個","要吃","麼辦","麼時","麼樣","麼好",
           "怎麼辦","什麼時","麼時候","可以嗎","要注意","比較好","吃什麼","是什麼","有什麼","為什麼",
           "要不要","需不需","可不可","會不會","該怎麼","怎麼樣","注意什"}

def plain(h):
    h = re.sub(r'<(script|style|svg)[^>]*>.*?</\1>', '', h, flags=re.S)
    h = re.sub(r'<li>', '・', h)
    h = re.sub(r'</(p|li|tr|h3|h4|div)>', '\n', h)
    h = re.sub(r'<[^>]+>', '', h)
    h = h.replace('&lt;','小於').replace('&gt;','大於').replace('&amp;','和').replace('&#8593;','')
    h = re.sub(r'[ \t]+', ' ', h)
    return re.sub(r'\n{2,}', '\n', h).strip()

def keywords(*parts):
    t = " ".join(parts)
    toks = set(re.findall(r'[A-Za-z]{3,}', t.lower()))
    cj = re.sub(r'[^一-鿿]', '', t)
    for n in (2, 3):
        for i in range(len(cj) - n + 1):
            w = cj[i:i+n]
            if w not in STOP and w not in STOP_NG: toks.add(w)
    return sorted(toks)

def extract(slug, extra=None):
    extra = extra or {}
    s = io.open(os.path.join(ROOT, slug, "index.html"), encoding="utf-8").read()
    secs = list(re.finditer(r'<h2 id="(s\d+)"[^>]*><span class="num">\d+</span>(.*?)</h2>', s))
    items = []
    for i, m in enumerate(secs):
        title = plain(m.group(2))
        end = secs[i+1].start() if i+1 < len(secs) else len(s)
        stop = re.search(r'<h2\b|<footer\b', s[m.end():end])   # 無 id 的 <h2>單張下載</h2>、頁尾都要擋掉
        if stop: end = m.end() + stop.start()
        body = s[m.end():end]
        body = re.sub(r'<(p|div) class="totop">.*?</\1>', '', body, flags=re.S)  # 濾掉「↑ 回目錄」錨點
        if "資料來源" in title:
            continue
        if "常見問題" in title:                      # 逐題拆成問答
            for q in re.finditer(r'<h3>(.*?)</h3>(.*?)(?=<h3>|<\w+ class="totop"|$)', body, re.S):
                qt, ans = plain(q.group(1)), plain(q.group(2))
                if qt and ans:
                    items.append({"q": qt, "a": ans, "k": keywords(qt, ans),
                                  "kx": keywords(qt), "src": "常見問題"})
        else:                                        # 整節做為一則可回答的內容
            lead = plain(body)
            if lead:
                ex = extra.get(title, [])
                kx = keywords(" ".join(ex)) if ex else []
                # 同義詞也要併進主關鍵詞，否則覆蓋率算不到，加權那關過不了
                items.append({"q": title, "a": lead[:700],
                              "k": sorted(set(keywords(title, lead[:400])) | set(kx)),
                              "kx": kx, "src": title})
    return items

PAGE = """<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>常見問題｜{topic}｜林祐賸醫師衛教</title>
<meta name="description" content="{topic} 常見問題互動問答，內容以本衛教詳細版為準。">
<link rel="stylesheet" href="assets/style.css">
<style>
.qa-box{{background:#fff;border:1.5px solid #cfe3da;border-radius:16px;padding:16px;margin:14px 0}}
.qa-box label{{display:block;font-weight:700;margin-bottom:8px;font-size:1.05rem}}
.qa-row{{display:flex;gap:8px}}
.qa-row input{{flex:1 1 auto;min-width:0;font:inherit;font-size:1.05rem;padding:11px 13px;
  border:1.5px solid #cfe3da;border-radius:11px}}
.qa-row button{{flex:0 0 auto;font:inherit;font-size:1.02rem;font-weight:700;padding:11px 18px;border:0;
  border-radius:11px;background:#2d6a4f;color:#fff;cursor:pointer}}
.chips{{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}}
.chips button{{font:inherit;font-size:.95rem;padding:9px 13px;border:1.5px solid #cfe3da;border-radius:999px;
  background:#f3faf6;color:#245341;cursor:pointer;text-align:left;line-height:1.4}}
.chips button:hover{{border-color:#2d6a4f}}
.answer{{margin-top:14px;padding:15px 17px;border-radius:14px;background:#eef7f2;border:1.5px solid #2d6a4f;
  font-size:1.05rem;line-height:1.95}}
.answer.none{{background:#fdf5e9;border-color:#e3cba1}}
.answer h3{{margin:0 0 .4em;font-size:1.08rem;color:#1f5d45}}
.answer p{{margin:.45em 0;white-space:pre-wrap}}
.answer .src{{margin-top:.7em;font-size:.88rem;color:#5d7268}}
.answer .speak{{margin-top:12px;font:inherit;font-size:1rem;font-weight:700;padding:9px 16px;border:1.5px solid #2d6a4f;
  border-radius:11px;background:#fff;color:#2d6a4f;cursor:pointer}}
</style></head>
<body><a class="skip" href="#main">跳到內容</a><div class="app">
<header class="topbar"><a href="index.html">← 回首頁</a><div class="title">{topic}</div></header>
<main id="main">
<div class="page-title"><span class="icon" aria-hidden="true">💬</span><h1>常見問題</h1></div>
<span class="topic-chip">可以直接問我</span>

<div class="qa-box">
<label for="q">想問什麼？打幾個字就好</label>
<div class="qa-row">
<input id="q" type="text" placeholder="例如：可以拔牙嗎" autocomplete="off" enterkeyhint="search">
<button id="go" type="button">問</button>
</div>
<div class="chips" id="chips"></div>
</div>

<div id="ans" hidden></div>

<p class="source-copy">這裡的回答<b>只來自本衛教專欄的內容</b>。如果問到專欄裡沒有的事情，系統會請您直接詢問主治醫師。</p>

<div class="pager"><a href="topic-{last}.html">← 上一頁</a><a class="next" href="index.html">回首頁 →</a></div>
<a class="download" href="handout.pdf" download>下載原始 A5 衛教單</a>
</main>
{navbar}
<script>
const KB = {kb};
const NONE = "本衛教專欄尚無可以回答您問題的資訊，請洽您的主治醫師詢問及討論。";
const STOPW = new Set(["可以","什麼","怎麼","要怎","如何","請問","我的","會不","不會","需要","應該","是不","有沒","沒有","哪些","多少","一下","的話","時候","可不","比較","這個","那個","要吃","麼辦","麼時","麼樣","麼好","麼辦","麼時","麼樣","麼好"]);
const STOP3 = new Set(["怎麼辦","什麼時","麼時候","可以嗎","要注意","比較好","吃什麼","是什麼","有什麼","為什麼","要不要","需不需","可不可","會不會","該怎麼","怎麼樣","注意什"]);
/* 回傳每個詞與其在提問中的位置，供計算字元覆蓋率 */
function grams(s){{
  const out = [];
  const low = s.toLowerCase();
  let m; const re = /[a-z]{{3,}}/g;
  while((m = re.exec(low)) !== null) out.push({{w:m[0], i:m.index, n:m[0].length, cj:false}});
  const cj = s.replace(/[^一-鿿]/g,"");
  for(const n of [2,3]) for(let i=0;i+n<=cj.length;i++){{
    const w = cj.slice(i,i+n);
    if(n===2 && STOPW.has(w)) continue;
    if(n===3 && STOP3.has(w)) continue;
    out.push({{w, i, n, cj:true}});
  }}
  const elen = (low.match(/[a-z]{{3,}}/g)||[]).join("").length;
  return {{list:out, len: cj.length + elen}};
}}
function ask(text){{
  const box = document.getElementById("ans");
  const q = (text||"").trim();
  if(!q){{ box.hidden = true; return; }}
  const g = grams(q);
  if(g.len === 0){{ box.hidden = true; return; }}
  let best = null, bestScore = 0;
  for(const item of KB){{
    const ks = new Set(item.k);
    const covered = new Set();
    for(const gi of g.list){{
      if(!ks.has(gi.w)) continue;
      for(let k=0;k<gi.n;k++) covered.add((gi.cj?"c":"e") + (gi.i + k));
    }}
    // 最長連續命中字數：避免單一個兩字詞（例如「美國」）就誤判為命中
    let run = 0, bestRun = 0;
    for(let k=0;k<g.len;k++){{
      if(covered.has("c"+k) || covered.has("e"+k)){{ run++; if(run>bestRun) bestRun=run; }}
      else run = 0;
    }}
    // 是否命中人工指定的同義詞（刻意指向該節，屬強訊號）
    let kxHit = false;
    if(item.kx && item.kx.length){{
      const kxs = new Set(item.kx);
      for(const gi of g.list){{ if(kxs.has(gi.w)){{ kxHit = true; break; }} }}
    }}
    let score = covered.size / g.len;
    // 至少要蓋到提問的 4 個字（短提問就看它自己的長度），人工同義詞也一樣要過這關
    if(covered.size < Math.min(4, g.len)) score = 0;
    // 命中太零碎就不算；但命中人工同義詞時豁免，並給予加權
    if(!kxHit && bestRun < 3 && score < 0.4) score = 0;
    if(kxHit && score > 0) score += 0.4;
    if(item.src === "常見問題") score *= 1.12;
    if(score > bestScore){{ bestScore = score; best = item; }}
  }}
  if(!best || bestScore < 0.45){{
    box.className = "answer none";
    box.innerHTML = "<h3>這個問題專欄裡沒有</h3><p>" + NONE + "</p>";
  }} else {{
    box.className = "answer";
    box.innerHTML = "<h3>" + best.q + "</h3><p>" + best.a.replace(/</g,"&lt;") + "</p>" +
      "<p class='src'>出處：本衛教詳細版　" + best.src + "</p>" +
      "<button class='speak' type='button' id='sp'>🔊 唸給我聽</button>";
    const sp = document.getElementById("sp");
    if(sp && window.speechSynthesis){{
      sp.addEventListener("click", function(){{
        speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(best.q + "。" + best.a);
        u.lang = "zh-TW"; u.rate = 0.85;
        const v = speechSynthesis.getVoices().find(x=>x.lang==="zh-TW"||x.lang==="zh_TW");
        if(v) u.voice = v;
        speechSynthesis.speak(u);
      }});
    }} else if(sp) {{ sp.hidden = true; }}
  }}
  box.hidden = false;
  box.scrollIntoView({{behavior:"smooth", block:"nearest"}});
}}
document.getElementById("go").addEventListener("click", ()=>ask(document.getElementById("q").value));
document.getElementById("q").addEventListener("keydown", e=>{{ if(e.key==="Enter") ask(e.target.value); }});
const chips = document.getElementById("chips");
KB.filter(i=>i.src==="常見問題").slice(0,6).forEach(i=>{{
  const b = document.createElement("button"); b.type="button"; b.textContent = i.q;
  b.addEventListener("click", ()=>{{ document.getElementById("q").value = i.q; ask(i.q); }});
  chips.appendChild(b);
}});
</script></body></html>
"""

def build_faq(slug, topic, n_sections, navbar_html, extra=None):
    items = extract(slug, extra)
    html = PAGE.format(topic=topic, last=n_sections, navbar=navbar_html,
                       kb=json.dumps(items, ensure_ascii=False))
    io.open(os.path.join(PREV, slug, "faq.html"), "w", encoding="utf-8").write(html)
    return len(items)
