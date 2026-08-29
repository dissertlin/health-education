# -*- coding: utf-8 -*-
"""在 A5 衛教單標題列右上角插入向量 QR code（可重複執行，會覆蓋舊的）。
用法: python3 add_qr.py <輸入.svg> <輸出.svg> <網址> [說明文字]
"""
import io, re, sys, segno

src, dst, url = sys.argv[1], sys.argv[2], sys.argv[3]
caption = sys.argv[4] if len(sys.argv) > 4 else u"掃描看電子版"

PANEL_X, PANEL_Y, PANEL_W, PANEL_H = 459.0, 18.0, 76.0, 76.0   # 標題列 x18..541 / y15..99
QR_SIZE = 64.0
QR_X = PANEL_X + (PANEL_W - QR_SIZE) / 2
QR_Y = PANEL_Y + 6.0

qr = segno.make(url, error='m')
m = [list(r) for r in qr.matrix]
n = len(m)
scale = QR_SIZE / n

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

block = (
    u'<!--QR--><g id="qr">'
    u'<text x="%g" y="%g" text-anchor="end" style="font:700 8.4px \'Microsoft JhengHei\',\'Noto Sans TC\',sans-serif;fill:#d8fbff">%s</text>'
    u'<rect x="%g" y="%g" width="%g" height="%g" rx="10" fill="#fff"/>'
    u'<g transform="translate(%g %g) scale(%.6f)" shape-rendering="crispEdges">'
    u'<path d="%s" fill="#10283a"/></g>'
    u'</g><!--/QR-->'
) % (PANEL_X - 9, PANEL_Y + PANEL_H / 2 + 3, caption,
     PANEL_X, PANEL_Y, PANEL_W, PANEL_H,
     QR_X, QR_Y, scale, "".join(d))

s = io.open(src, encoding="utf-8").read()
s = re.sub(r'<!--QR-->.*?<!--/QR-->', '', s, flags=re.S)      # 新版標記
s = re.sub(r'<g id="qr">.*?</text></g>', '', s, flags=re.S)   # 舊版殘留
anchor = '<rect x="18" y="15" width="523" height="84" rx="16" fill="url(#g)"/>'
assert s.count(anchor) == 1, "找不到標題列"
assert s.count('id="qr"') == 0, "舊 QR 未清乾淨"
s = s.replace(anchor, anchor + block)
io.open(dst, "w", encoding="utf-8").write(s)
print(u"QR v%s (%dx%d) | 網址 %d 字 | 列印邊長 %.1f mm | 每模組 %.2f mm"
      % (qr.version, n, n, len(url), QR_SIZE * 148.0 / 559.0, scale * 148.0 / 559.0))
