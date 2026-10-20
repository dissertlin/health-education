# -*- coding: utf-8 -*-
"""以 Azure 語音服務產生語音版音檔，與既有 10 份使用同一個聲音。

金鑰只從環境變數讀，不寫進程式，也不要貼進對話或 shell 歷史：

    read -rs SPEECH_KEY && export SPEECH_KEY SPEECH_REGION=japaneast
    python3 -I tools/voice_tts.py --all

讀 patient-education-preview/<slug>/transcripts/*.txt，輸出同名 .mp3 至 audio/。
聲音：zh-TW-HsiaoChenNeural（台灣中文女聲）　語速：-15%（0.85 倍）
格式：MP3 24kHz 48kbps mono，與既有 10 個主題一致（實測確認過，非 16kHz/32kbps）。
已存在的 .mp3 預設略過，加 --force 才覆寫。

只用標準函式庫，不需要 pip install。
"""
import os, sys, glob, io, time, urllib.request, urllib.error

VOICE, RATE = "zh-TW-HsiaoChenNeural", "-15%"
FORMAT = "audio-24khz-48kbitrate-mono-mp3"
NEW = {"angina", "anticoag", "cath", "dm", "ep", "lipid", "mi"}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREV = os.path.join(ROOT, "patient-education-preview")

def ssml(text):
    body = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                .replace("\n", '<break time="400ms"/>'))
    return (f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-TW">'
            f'<voice name="{VOICE}"><prosody rate="{RATE}">{body}</prosody></voice></speak>')

def synth(endpoint, key, text):
    """單次合成；遇到 429／5xx 退避重試。"""
    req = urllib.request.Request(endpoint, data=ssml(text).encode("utf-8"), method="POST",
        headers={"Ocp-Apim-Subscription-Key": key,
                 "Content-Type": "application/ssml+xml",
                 "X-Microsoft-OutputFormat": FORMAT,
                 "User-Agent": "health-education-voice"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 4:
                time.sleep(2 ** attempt); continue
            raise RuntimeError(f"HTTP {e.code}: {e.read()[:200].decode('utf-8','replace')}")
    raise RuntimeError("重試多次仍失敗")

def main():
    key, region = os.environ.get("SPEECH_KEY"), os.environ.get("SPEECH_REGION")
    if not (key and region):
        sys.exit("請先設定環境變數 SPEECH_KEY 與 SPEECH_REGION（例如 japaneast）")
    endpoint = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    slugs = args or sorted(NEW)

    made = skipped = failed = 0
    for slug in slugs:
        tdir = os.path.join(PREV, slug, "transcripts")
        if not os.path.isdir(tdir):
            print(f"  ! {slug}：找不到 transcripts/"); continue
        adir = os.path.join(PREV, slug, "audio"); os.makedirs(adir, exist_ok=True)
        for t in sorted(glob.glob(os.path.join(tdir, "*.txt"))):
            name = os.path.basename(t)[:-4]
            out = os.path.join(adir, name + ".mp3")
            if os.path.exists(out) and not force:
                skipped += 1; continue
            text = io.open(t, encoding="utf-8").read().strip()
            try:
                audio = synth(endpoint, key, text)
            except Exception as e:
                print(f"  ✗ {slug}/{name}：{e}"); failed += 1; continue
            if not audio.startswith(b"ID3") and audio[:1] != b"\xff":
                print(f"  ✗ {slug}/{name}：回應不是 MP3"); failed += 1; continue
            open(out, "wb").write(audio)
            print(f"  ✓ {slug}/{name}.mp3  {len(text)} 字  {len(audio)/1024:.0f} KB"); made += 1
    print(f"\n完成：新增 {made}、略過 {skipped}、失敗 {failed}")

main()
