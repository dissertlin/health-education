#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把瀏覽次數計數器裝到／移出十份衛教詳細版。

用法：
    python3 tools/counter/add_counter.py https://he-counter.你的帳號.workers.dev
    python3 tools/counter/add_counter.py --remove

插入的內容以 <!-- 瀏覽次數 begin/end --> 包住，移除時整段刪掉，不影響其他內容。
每一份頁面各自帶自己的頁面代號，所以是各自獨立計數。
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAGES = ["af", "af-intro", "af-meds", "bp", "brady",
         "ep", "gout", "hf", "lipid", "oh", "pacemaker", "svt"]

CSS_BEGIN = "  /* 瀏覽次數 begin */"
CSS = """  /* 瀏覽次數 begin */
  .views{margin:.9em 0 0;font-size:.78rem;color:var(--sub)}
  .views b{color:var(--brand);font-weight:700}
  /* 瀏覽次數 end */
"""

HTML = """<!-- 瀏覽次數 begin -->
<p class="views" id="pv" hidden>本頁已被瀏覽 <b id="pvn">—</b> 次</p>
<script>
(function(){
  var API=%(api)s, P=%(page)s;
  var box=document.getElementById("pv"), num=document.getElementById("pvn");
  if(!box||!num||!window.fetch) return;
  fetch(API+"/hit?p="+P,{method:"POST",cache:"no-store",mode:"cors"})
    .then(function(r){ return r.ok ? r.json() : null; })
    .then(function(d){
      if(d && typeof d.n==="number"){
        num.textContent=d.n.toLocaleString("zh-TW");
        box.hidden=false;            /* 只有成功拿到數字才顯示 */
      }
    })
    .catch(function(){});            /* 失敗就靜靜不顯示，不影響閱讀 */
})();
</script>
<!-- 瀏覽次數 end -->
"""


def strip_block(s, begin, end):
    while begin in s and end in s:
        a = s.index(begin)
        b = s.index(end, a) + len(end)
        while b < len(s) and s[b] == "\n":
            b += 1
        s = s[:a] + s[b:]
    return s


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    arg = sys.argv[1]
    remove = (arg == "--remove")
    api = arg.rstrip("/") if not remove else ""
    if not remove and not re.match(r"^https://[\w.-]+/?$", arg.rstrip("/") + "/"):
        print("網址看起來不對，應該像 https://he-counter.你的帳號.workers.dev")
        return 1

    for p in PAGES:
        f = os.path.join(ROOT, p, "index.html")
        s = io.open(f, encoding="utf-8").read()
        s = strip_block(s, CSS_BEGIN, "  /* 瀏覽次數 end */")
        s = strip_block(s, "<!-- 瀏覽次數 begin -->", "<!-- 瀏覽次數 end -->")
        if not remove:
            anchor = "</style>"
            assert anchor in s, p
            s = s.replace(anchor, CSS + anchor, 1)
            block = HTML % {"api": '"%s"' % api, "page": '"%s"' % p}
            m = re.search(r"</footer>", s)
            assert m, p
            s = s[:m.start()] + block + s[m.start():]
        io.open(f, "w", encoding="utf-8").write(s)
        print(("移除 " if remove else "裝上 ") + p)
    print("完成 %d 份" % len(PAGES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
