#!/usr/bin/env python3
"""檢查站內 HTML 的相對連結、錨點、資源是否存在；並列出外部連結。
用法：python3 tools/audit_links.py [--external]
"""
import sys, re, os
from pathlib import Path
from urllib.parse import urlparse, unquote
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parent.parent

class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.refs=[]; s.ids=set()
    def handle_starttag(s, tag, a):
        a = dict(a)
        if a.get('id'): s.ids.add(a['id'])
        if tag=='a' and a.get('name'): s.ids.add(a['name'])
        for k in ('href','src','poster'):
            if a.get(k) is not None: s.refs.append((tag,k,a[k]))
        if tag=='link' and a.get('href') is None: pass
        if a.get('srcset'):
            for part in a['srcset'].split(','):
                s.refs.append((tag,'srcset',part.strip().split()[0]))

def parse(path):
    p=P(); p.feed(path.read_text(encoding='utf-8')); return p

def main():
    ext = '--external' in sys.argv
    pages = {f: parse(f) for f in ROOT.rglob('*.html') if '.git' not in f.parts}
    problems=[]; externals={}
    for f,p in pages.items():
        for tag,k,v in p.refs:
            if not v or v.startswith(('mailto:','tel:','javascript:','data:')): continue
            u=urlparse(v)
            if u.scheme in ('http','https'):
                externals.setdefault(v,[]).append(str(f.relative_to(ROOT))); continue
            if v.startswith('#'):
                if v[1:] and v[1:] not in p.ids and unquote(v[1:]) not in p.ids:
                    problems.append((f,v,'錨點不存在'))
                continue
            if u.scheme or v.startswith('//'): continue
            target = (f.parent / unquote(u.path)) if not u.path.startswith('/') else ROOT/u.path.lstrip('/')
            if target.is_dir(): target = target/'index.html'
            if not target.exists():
                problems.append((f,v,'檔案不存在')); continue
            if u.fragment and target.suffix=='.html' and target in pages:
                if unquote(u.fragment) not in pages[target].ids:
                    problems.append((f,v,'目標頁錨點不存在'))
    for f,v,why in sorted(problems):
        print(f'{f.relative_to(ROOT)}: {v}  [{why}]')
    print(f'\n頁面 {len(pages)}，站內問題 {len(problems)}，外部連結 {len(externals)} 種')
    if ext:
        for u,fs in sorted(externals.items()): print(u, len(fs), fs[0])
    return 1 if problems else 0
sys.exit(main())
