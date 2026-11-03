#!/usr/bin/env python3
"""啟發式文字檢查（只列出可疑處供人工判斷，不會修改任何檔案）。
檢查：重複字詞、連續標點、中文旁的半形標點、簡體字、常見誤用字、全形/半形空白異常。
用法：python3 tools/audit_text.py [路徑...]
"""
import sys, re
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parent.parent

class T(HTMLParser):
    def __init__(s): super().__init__(); s.out=[]; s.skip=0
    def handle_starttag(s,t,a):
        if t in('script','style'): s.skip+=1
    def handle_endtag(s,t):
        if t in('script','style'): s.skip=max(0,s.skip-1)
    def handle_data(s,d):
        if not s.skip: s.out.append(d)

SIMPLIFIED = set('这个们说话为术么时间来对发过还问题经应该护药务开关页点体电图种让给边带终买卖师热报参观阳阴阶线级织绍续总结编统网络应机选择环态现实医疗别压测维养脑动强护让错项饮觉复习读写')
# 繁體中與簡體相同的字不列入（如 "医" 以外）
SIMP_ONLY = set('这个们说话为术么时间来对发过还问题经应该护药务开关页点体电图种让给边带终买卖师热报参观阳阴阶线级织绍续总结编统网络机选择环态现实医疗别压测维养脑动强错项饮觉复习读写')
SIMP_ONLY -= set('')  # placeholder
PATTERNS = [
 (r'([一-鿿])\1{2,}', '同字連續 3 次以上'),
 (r'(的的|了了|是是|在在|和和|或或|與與|及及|可以可以|需要需要)', '疊字'),
 (r'[，。、；：！？]{2,}(?![」』）])', '連續全形標點'),
 (r'(?<=[一-鿿]),(?=[一-鿿])', '中文間半形逗號'),
 (r'(?<=[一-鿿])\?(?![\w=&/])', '中文後半形問號'),
 (r'(?<=[一-鿿]);', '中文後半形分號'),
 (r'(?<=[一-鿿])\.(?=\s|$)', '中文後半形句點'),
 (r'\(([^()]*[一-鿿][^()]*)\)', '中文括號使用半形'),
 (r'[ \t]{2,}', '連續空白'),
 (r'。。|，，|、、', '重複標點'),
 (r'(?:再)(?:次|度)?見[^面]', None),
 (r'(?<![不])作[用]的', None),
 (r'像是例如|例如像是|比如例如', '贅詞'),
 (r'(?:服藥|吃藥|用藥)的(?:時候|時間)點', None),
 (r'心室上頻脈', '術語「心室上頻脈」：臨床慣用為「上心室頻脈／陣發性上心室心搏過速」，僅標註'),
 (r'(?<![一-鿿])(?:註：|注:)', None),
 (r'\b(\w{3,})\s+\1\b', '英文重複詞'),
 (r'[Ａ-Ｚａ-ｚ０-９]', '全形英數字'),
 (r'(?:纇|錶準|標準準|既使|按步就班|必需品要|以經|在次|在試|做為|佈|瞭解)', '常見錯別字候選（佈/瞭解/做為 等僅供參考）'),
 (r'(?:的|得|地)(?=[，。])', None),
]

def check(path):
    p=T(); p.feed(path.read_text(encoding='utf-8'))
    text='\n'.join(p.out)
    hits=[]
    for ln,line in enumerate(text.split('\n'),1):
        s=line.strip()
        if not s: continue
        for pat,msg in PATTERNS:
            if msg is None: continue
            for m in re.finditer(pat,s):
                hits.append((msg,s[max(0,m.start()-14):m.end()+14],))
        sim=[c for c in s if c in SIMP_ONLY]
        if sim: hits.append(('疑似簡體字 '+''.join(sorted(set(sim))),s[:40]))
    return hits

def main():
    args=[Path(a) for a in sys.argv[1:]] or [ROOT]
    files=[]
    for a in args:
        files += [a] if a.is_file() else sorted(a.rglob('*.html'))
    total=0
    for f in files:
        if '.git' in f.parts: continue
        for msg,ctx in check(f):
            total+=1; print(f'{f.relative_to(ROOT)}\t{msg}\t…{ctx}…')
    print(f'\n可疑處 {total}')
main()
