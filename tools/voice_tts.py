# -*- coding: utf-8 -*-
"""以 Azure 語音服務產生語音版音檔，與既有 10 份使用同一個聲音與語速。

    export SPEECH_KEY=<你的金鑰>
    export SPEECH_REGION=<你的區域，例如 eastasia>
    pip install azure-cognitiveservices-speech
    python3 tools/voice_tts.py anticoag          # 單一主題
    python3 tools/voice_tts.py --all             # 全部尚未產生的主題

讀 patient-education-preview/<slug>/transcripts/*.txt，輸出同名 .mp3 至 audio/。
聲音：zh-TW-HsiaoChenNeural（台灣中文女聲）　語速：-25%　格式：MP3 16kHz 32kbps mono
已存在的 .mp3 預設略過，加 --force 才覆寫。
"""
import os, sys, glob, io

VOICE, RATE = "zh-TW-HsiaoChenNeural", "-25%"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREV = os.path.join(ROOT, "patient-education-preview")

def ssml(text):
    body = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                .replace("\n", '<break time="400ms"/>'))
    return (f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-TW">'
            f'<voice name="{VOICE}"><prosody rate="{RATE}">{body}</prosody></voice></speak>')

def main():
    try:
        import azure.cognitiveservices.speech as speechsdk
    except ImportError:
        sys.exit("請先安裝：pip install azure-cognitiveservices-speech")
    key, region = os.environ.get("SPEECH_KEY"), os.environ.get("SPEECH_REGION")
    if not (key and region):
        sys.exit("請先設定環境變數 SPEECH_KEY 與 SPEECH_REGION")

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    slugs = args or [os.path.basename(d) for d in sorted(glob.glob(os.path.join(PREV, "*")))
                     if os.path.isdir(os.path.join(d, "transcripts"))]

    cfg = speechsdk.SpeechConfig(subscription=key, region=region)
    cfg.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)

    made = skipped = failed = 0
    for slug in slugs:
        tdir = os.path.join(PREV, slug, "transcripts")
        adir = os.path.join(PREV, slug, "audio"); os.makedirs(adir, exist_ok=True)
        for t in sorted(glob.glob(os.path.join(tdir, "*.txt"))):
            name = os.path.basename(t)[:-4]
            out = os.path.join(adir, name + ".mp3")
            if os.path.exists(out) and not force:
                skipped += 1; continue
            text = io.open(t, encoding="utf-8").read().strip()
            syn = speechsdk.SpeechSynthesizer(
                speech_config=cfg, audio_config=speechsdk.audio.AudioOutputConfig(filename=out))
            r = syn.speak_ssml_async(ssml(text)).get()
            if r.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print(f"  ✓ {slug}/{name}.mp3  ({len(text)} 字)"); made += 1
            else:
                print(f"  ✗ {slug}/{name}：{r.reason} {getattr(r,'error_details','')}"); failed += 1
    print(f"\n完成：新增 {made}、略過 {skipped}、失敗 {failed}")
    print("提醒：預建神經語音的商業使用權僅授予付費層，請確認您的訂閱層級。")

if __name__ == "__main__":
    main()
