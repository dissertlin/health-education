# -*- coding: utf-8 -*-
"""在 A5 衛教單上插入向量 QR code（可重複執行，會自動覆蓋舊的）。

用法:
  python3 add_qr.py 輸入.svg 輸出.svg 網址 [選項]

選項:
  --caption 文字        QR 下方／左方說明（預設「掃描看電子版」，空字串則不加）
  --x --y --size        QR 白底面板左上角座標與 QR 邊長（viewBox 單位）
  --caption-pos below|left   說明文字位置（預設 below）
  --caption-fill 色碼   說明文字顏色（深色底建議淺色字）
  --panel-stroke 色碼   白底面板外框（淺色底建議加，深色底可省略 none）
"""
import argparse, io, re, segno

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst"); ap.add_argument("url")
ap.add_argument("--caption", default=u"掃描看電子版")
ap.add_argument("--x", type=float, default=459.0)
ap.add_argument("--y", type=float, default=18.0)
ap.add_argument("--size", type=float, default=64.0)
ap.add_argument("--pad", type=float, default=6.0)
ap.add_argument("--caption-pos", default="below", choices=["below", "left"])
ap.add_argument("--caption-fill", default="#176d8e")
ap.add_argument("--panel-stroke", default="none")
ap.add_argument("--page-mm", type=float, default=148.0)
ap.add_argument("--viewbox-w", type=float, default=559.0)
a = ap.parse_args()

pw = ph = a.size + a.pad * 2
qx, qy = a.x + a.pad, a.y + a.pad

qr = segno.make(a.url, error='m')
m = [list(r) for r in qr.matrix]
n = len(m)
scale = a.size / n

d = []
for y in range(n):
    x = 0
    while x < n:
        if m[y][x]:
            run = 1
            while x + run < n and m[y][x + run]:
                run += 1
            d.append("M%d %dh%dv1h-%dz" % (x, y, run, run))
            x += run
        else:
            x += 1

cap = u''
if a.caption:
    style = (u"font:700 8.4px 'Microsoft JhengHei','Noto Sans TC',sans-serif;fill:%s"
             % a.caption_fill)
    if a.caption_pos == "below":
        cap = (u'<text x="%g" y="%g" text-anchor="middle" style="%s">%s</text>'
               % (a.x + pw / 2, a.y + ph + 10, style, a.caption))
    else:
        cap = (u'<text x="%g" y="%g" text-anchor="end" style="%s">%s</text>'
               % (a.x - 9, a.y + ph / 2 + 3, style, a.caption))

block = (
    u'<!--QR--><g id="qr">%s'
    u'<rect x="%g" y="%g" width="%g" height="%g" rx="10" fill="#fff" stroke="%s"/>'
    u'<g transform="translate(%g %g) scale(%.6f)" shape-rendering="crispEdges">'
    u'<path d="%s" fill="#10283a"/></g></g><!--/QR-->'
) % (cap, a.x, a.y, pw, ph, a.panel_stroke, qx, qy, scale, "".join(d))

s = io.open(a.src, encoding="utf-8").read()
s = re.sub(r'<!--QR-->.*?<!--/QR-->', '', s, flags=re.S)
assert s.count('id="qr"') == 0, u"舊 QR 未清乾淨"
i = s.rindex('</svg>')                       # 插在最後，畫在所有元素之上
s = s[:i] + block + s[i:]
io.open(a.dst, "w", encoding="utf-8").write(s)

mm = a.page_mm / a.viewbox_w
print(u"QR v%s (%dx%d) | 網址 %d 字 | 列印邊長 %.1f mm | 每模組 %.2f mm"
      % (qr.version, n, n, len(a.url), a.size * mm, scale * mm))
