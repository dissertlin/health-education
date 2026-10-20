# -*- coding: utf-8 -*-
"""語音版產生器：依詳細版的分節，產出與既有 10 份相同結構的語音版主題資料夾。

用法：python3 tools/voice_gen.py <slug>
資料來源：tools/voice_scripts/<slug>.py（逐字稿，以台灣口語撰寫）
產出：patient-education-preview/<slug>/

音檔（audio/*.mp3）不由本程式產生，需另行以 TTS 製作後放入 audio/。
"""
import io, json, os, re, shutil, sys, importlib.util

RATE = 2.77   # 字／秒，實測自既有 56 個 Azure zh-TW-HsiaoChenNeural（rate -25%）音檔
LIMIT = 332   # 2 分鐘上限

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREV = os.path.join(ROOT, "patient-education-preview")
TEMPLATE_ASSETS = os.path.join(PREV, "svt", "assets")

def esc(t):
    return (t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))

HEAD = ('<!doctype html>\n<html lang="zh-Hant"><head><meta charset="utf-8">'
 '<meta name="viewport" content="width=device-width,initial-scale=1">'
 '<title>{title}｜林祐賸醫師衛教</title>'
 '<meta name="description" content="{topic}，提供分頁閱讀、台灣中文女聲朗讀與互動問答。">'
 '<link rel="stylesheet" href="assets/style.css"></head>\n')

def navbar(secs, active):
    out=[f'<nav class="navbar" aria-label="分頁導覽"><a href="index.html" aria-label="主題首頁"'
         + (' class="active" aria-current="page"' if active=="home" else '') + '>⌂</a>']
    for i,s in enumerate(secs,1):
        cur=' class="active" aria-current="page"' if active==i else ''
        out.append(f'<a href="topic-{i}.html" aria-label="{esc(s["title"])}"{cur}>{i}</a>')
    cur=' class="active" aria-current="page"' if active=="faq" else ''
    out.append(f'<a href="faq.html" aria-label="常見問題"{cur}>?</a>')
    out.append('</nav>')
    return "".join(out)

def panels(T):
    return ('<a class="download" href="handout.pdf" download>下載原始 A5 衛教單</a>'
      '<details class="source-panel"><summary>查看原始衛教圖卡</summary><figure>'
      '<a href="assets/handout.png" target="_blank" rel="noopener">'
      f'<img src="assets/handout.png" alt="{esc(T["topic"])}原始衛教單" loading="lazy" width="840" height="1190">'
      '</a><figcaption>點選圖卡可開啟大圖。</figcaption></figure></details>'
      '<details class="source-panel"><summary>原稿來源與說明</summary>'
      f'<div class="source-credits">{esc(T["footer"])}</div></details>')

def check_length(T):
    """逐字稿長度稽核：任何一段超過 2 分鐘就中止，避免產出過長的音檔。"""
    bad=[]
    def n(t): return len(re.sub(r"\s","",t))
    for label, txt in [("導讀", T["summary"])] + [(f'第{i}節 {s["title"]}', s["text"])
                                                  for i,s in enumerate(T["sections"],1)]:
        c=n(txt)
        if c > LIMIT: bad.append(f'{label}：{c} 字，約 {c/RATE:.0f} 秒（上限 {LIMIT} 字／120 秒）')
    if bad:
        raise SystemExit("逐字稿過長，請精簡後再產生：\n  " + "\n  ".join(bad))

def build(T):
    check_length(T)
    slug=T["slug"]; secs=T["sections"]; out=os.path.join(PREV, slug)
    os.makedirs(os.path.join(out,"audio"), exist_ok=True)
    os.makedirs(os.path.join(out,"transcripts"), exist_ok=True)
    if not os.path.isdir(os.path.join(out,"assets")):
        shutil.copytree(TEMPLATE_ASSETS, os.path.join(out,"assets"))

    # ---- 首頁 ----
    tiles="".join(
      f'<a class="tile" href="topic-{i}.html"><span class="topic-number">{i}</span>'
      f'<span class="icon" aria-hidden="true">{s["icon"]}</span><b>{esc(s["title"])}</b>'
      '<span class="tile-cta">點我查看 →</span></a>' for i,s in enumerate(secs,1))
    tiles+=('<a class="tile" href="faq.html"><span class="topic-number">?</span>'
            '<span class="icon" aria-hidden="true">💬</span><b>常見問題（可以問我）</b>'
            '<span class="tile-cta">點我查看 →</span></a>')
    html=(HEAD.format(title=T["topic"], topic=T["topic"])
      + '<body><a class="skip" href="#main">跳到內容</a><div class="app">'
      f'<header class="topbar home-topbar"><div class="title">{esc(T["topic"])}</div></header><main id="main">'
      f'<section class="hero"><h1>{esc(T["topic"])}</h1><h2>林祐賸醫師衛教 ♥</h2></section>'
      '<section class="doctor-card"><img src="assets/doctor_avatar.png" alt="林醫師可愛圖像" width="96" height="96">'
      '<div><b>一個主題，一個主題慢慢看</b><p>每頁都有完整文字，也可以按下按鈕用聽的。</p></div></section>'
      '<section class="audio-wrap" data-src="audio/summary.mp3" aria-label="台灣中文女聲朗讀">'
      '<div class="audio-heading"><img src="assets/doctor_avatar.png" alt="">'
      '<div><small>先聽導讀，再選下面的主題</small><strong>用聽的，也能了解</strong></div></div>'
      '<button class="audio-main" type="button" data-action="toggle" data-idle-label="按這裡聽導讀" aria-pressed="false">'
      '<span class="round" aria-hidden="true">🔊</span><span class="label">按這裡聽導讀</span></button>'
      '<button class="audio-repeat" type="button" data-action="repeat">↻ 從頭重播</button>'
      '<p class="audio-status" role="status" aria-live="polite">尚未播放</p></section>'
      f'<div class="intro-copy" data-source="intro">{esc(T["intro"])}</div>'
      '<div class="section-title">選擇想看的主題</div>'
      f'<section class="grid" aria-label="衛教分頁">{tiles}</section>'
      + panels(T)
      + '<a class="text-link" href="../index.html">← 回主題總覽</a></main>'
      + navbar(secs,"home")
      + '<script src="assets/audio-player.js"></script></body></html>')
    io.open(os.path.join(out,"index.html"),"w",encoding="utf-8").write(html)

    # ---- 各分頁 ----
    n=len(secs)
    for i,s in enumerate(secs,1):
        prev = 'index.html' if i==1 else f'topic-{i-1}.html'
        nxt  = 'faq.html' if i==n else f'topic-{i+1}.html'
        nxt_label = '常見問題 →' if i==n else '下一頁 →'
        html=(HEAD.format(title=s["title"], topic=T["topic"])
          + '<body><a class="skip" href="#main">跳到內容</a><div class="app">'
          f'<header class="topbar"><a href="index.html">← 回首頁</a><div class="title">{esc(T["topic"])}</div></header>'
          f'<main id="main"><div class="page-title"><span class="icon" aria-hidden="true">{s["icon"]}</span>'
          f'<h1>{esc(s["title"])}</h1></div><span class="topic-chip">主題 {i}／{n}</span>'
          f'<section class="audio-wrap" data-src="audio/topic-{i}.mp3" aria-label="台灣中文女聲朗讀">'
          '<button class="audio-main" type="button" data-action="toggle" data-idle-label="按這裡聽本頁" aria-pressed="false">'
          '<span class="round" aria-hidden="true">🔊</span><span class="label">按這裡聽本頁</span></button>'
          '<button class="audio-repeat" type="button" data-action="repeat">↻ 從頭重播</button>'
          '<p class="audio-status" role="status" aria-live="polite">尚未播放</p></section>'
          f'<section class="source-copy" aria-label="本頁文字" data-source="section">{esc(s["text"])}</section>'
          f'<div class="pager"><a href="{prev}">← 上一頁</a><a class="next" href="{nxt}">{nxt_label}</a></div>'
          + panels(T) + '</main>' + navbar(secs,i)
          + '<script src="assets/audio-player.js"></script></body></html>')
        io.open(os.path.join(out,f"topic-{i}.html"),"w",encoding="utf-8").write(html)
        io.open(os.path.join(out,"transcripts",f"topic-{i}.txt"),"w",encoding="utf-8").write(s["text"]+"\n")
    io.open(os.path.join(out,"transcripts","summary.txt"),"w",encoding="utf-8").write(T["summary"]+"\n")

    # ---- source-content.json ----
    json.dump({"slug":slug,"title":T["topic"],"intro":T["intro"],"footer":T["footer"],
               "summary":T["summary"],
               "sections":[{"number":i,"title":s["title"],"text":s["text"]} for i,s in enumerate(secs,1)]},
              io.open(os.path.join(out,"source-content.json"),"w",encoding="utf-8"),
              ensure_ascii=False, indent=1)
    # ---- 互動問答頁 ----
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    from voice_faq import build_faq
    n_kb = build_faq(slug, T["topic"], len(secs), navbar(secs, "faq"), T.get("faq_keywords"))
    return out, len(secs), n_kb

if __name__=="__main__":
    slug=sys.argv[1]
    spec=importlib.util.spec_from_file_location("sc", os.path.join(ROOT,"tools","voice_scripts",slug+".py"))
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    out,n,kb=build(mod.TOPIC)
    secs=mod.TOPIC["sections"]
    print(f"✓ {slug}：{n} 個分頁 + 互動問答（知識庫 {kb} 則）")
    for i,s_ in enumerate(secs,1):
        c=len(re.sub(r"\s","",s_["text"]))
        print(f"   第{i}節 {c:>4} 字　約 {c/RATE:>3.0f} 秒　{s_['title']}")
