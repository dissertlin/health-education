# -*- coding: utf-8 -*-
"""把 Speech Studio 匯出的 MP3 放進各主題的 audio/。

Speech Studio 匯出的檔名沿用上傳時的 <slug>__<name>.txt，所以下載回來會是
<slug>__<name>.mp3，例如 anticoag__topic-1.mp3 → anticoag/audio/topic-1.mp3。

用法：python3 -I tools/voice_install.py <解壓後的資料夾或 zip>
"""
import os, re, shutil, sys, zipfile, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREV = os.path.join(ROOT, "patient-education-preview")
SLUGS = {"angina","anticoag","cath","dm","ep","lipid","mi"}

def collect(src):
    """zip 直接讀，資料夾就走訪；只收 <slug>__<name>.mp3。"""
    if src.lower().endswith(".zip"):
        d = tempfile.mkdtemp(prefix="voice_mp3_")
        with zipfile.ZipFile(src) as z:
            z.extractall(d)          # 只解壓自己剛匯出的音檔
        src = d
    found = {}
    for dirpath, _, files in os.walk(src):
        for f in files:
            m = re.fullmatch(r"([a-z]+)__(summary|topic-\d+)\.mp3", f)
            if m and m.group(1) in SLUGS:
                found[(m.group(1), m.group(2))] = os.path.join(dirpath, f)
    return found

def main():
    if len(sys.argv) != 2:
        sys.exit("用法：python3 -I tools/voice_install.py <資料夾或 zip>")
    found = collect(sys.argv[1])

    expect = set()
    for slug in sorted(SLUGS):
        n = len([f for f in os.listdir(os.path.join(PREV, slug)) if re.fullmatch(r"topic-\d+\.html", f)])
        expect.add((slug, "summary"))
        expect |= {(slug, f"topic-{i}") for i in range(1, n + 1)}

    missing, extra = expect - set(found), set(found) - expect
    for slug, name in sorted(found):
        if (slug, name) not in expect:
            continue
        dst = os.path.join(PREV, slug, "audio")
        os.makedirs(dst, exist_ok=True)
        shutil.copy2(found[(slug, name)], os.path.join(dst, name + ".mp3"))

    print(f"放入 {len(expect & set(found))} / {len(expect)} 個音檔")
    if missing: print("缺少：", ", ".join(f"{s}/{n}" for s, n in sorted(missing)))
    if extra:   print("多出（已略過）：", ", ".join(f"{s}/{n}" for s, n in sorted(extra)))
    for slug in sorted(SLUGS):
        d = os.path.join(PREV, slug, "audio")
        c = len([f for f in os.listdir(d) if f.endswith(".mp3")]) if os.path.isdir(d) else 0
        print(f"  {slug:9s} {c} 個")

main()
