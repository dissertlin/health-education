#!/usr/bin/env python3
"""結構／無障礙／效能的靜態檢查。用法：python3 tools/audit_a11y.py"""
import re, sys
from pathlib import Path
from collections import Counter, defaultdict
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parent.parent
issues = defaultdict(list)
for f in sorted(ROOT.rglob('*.html')):
    if '.git' in f.parts: continue
    rel = str(f.relative_to(ROOT))
    s = BeautifulSoup(f.read_text(encoding='utf-8'), 'html.parser')
    h = s.find('html')
    if not h or not h.get('lang'): issues['缺 <html lang>'].append(rel)
    if not s.find('meta', attrs={'name':'viewport'}): issues['缺 viewport'].append(rel)
    if not s.title or not s.title.get_text(strip=True): issues['缺 title'].append(rel)
    if not s.find('meta', attrs={'name':'description'}): issues['缺 meta description'].append(rel)
    if not s.find('link', rel='icon'): issues['缺 favicon'].append(rel)
    if not s.find('main'): issues['缺 <main>'].append(rel)
    if len(s.find_all('h1')) != 1: issues['h1 不是剛好 1 個'].append(rel)
    prev = 0
    for t in s.find_all(re.compile('^h[1-6]$')):
        n = int(t.name[1]); 
        if prev and n > prev + 1: issues['標題層級跳級'].append(rel); break
        prev = n
    ids = [t['id'] for t in s.find_all(id=True)]
    if len(ids) != len(set(ids)): issues['重複 id'].append(rel)
    for im in s.find_all('img'):
        if im.get('alt') is None: issues['img 缺 alt'].append(rel); break
    for im in s.find_all('img'):
        if not (im.get('width') and im.get('height')): issues['img 缺 width/height（版面位移）'].append(rel); break
    for im in s.find_all('img'):
        if im.get('loading') != 'lazy' and 'logo' not in (im.get('src') or '') : issues['img 未 lazy'].append(rel); break
    for a in s.find_all('a'):
        if not a.get_text(strip=True) and not a.get('aria-label') and not a.find('img', alt=True): issues['連結無可辨識名稱'].append(rel); break
    for b in s.find_all('button'):
        if not b.get_text(strip=True) and not b.get('aria-label'): issues['按鈕無名稱'].append(rel); break
    for sv in s.find_all('svg'):
        if not (sv.get('aria-hidden') == 'true' or sv.get('role') or sv.find('title')): issues['svg 無 aria-hidden/role'].append(rel); break
    if not s.find(href='#main') and not s.find(class_=re.compile('skip')): issues['缺 skip link'].append(rel)
    for t in s.find_all('table'):
        if not t.find('th'): issues['table 缺 th'].append(rel); break
    for a in s.find_all('a', target='_blank'):
        if 'noopener' not in (a.get('rel') or []): issues['target=_blank 缺 noopener'].append(rel); break
    if s.find('audio') and not s.find('audio').get('preload'): issues['audio 未設 preload'].append(rel)
for k, v in sorted(issues.items(), key=lambda x: -len(x[1])):
    print(f'{k}: {len(v)}'); 
    if '-v' in sys.argv: [print('   ', x) for x in v]
    else: print('    e.g.', ', '.join(v[:3]))
