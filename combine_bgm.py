"""
clips/ 内のwavファイルをランダム順にクロスフェードで繋ぎ、
約1時間のBGM (output/full_bgm.mp3) を作る。
"""

import os
import random
from pydub import AudioSegment

CLIPS_DIR = "clips"
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "full_bgm.mp3")

TARGET_MS = 60 * 60 * 1000  # 1時間
CROSSFADE_MS = 3000  # クロスフェード3秒


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    clip_paths = [
        os.path.join(CLIPS_DIR, f)
        for f in os.listdir(CLIPS_DIR)
        if f.endswith(".wav")
    ]
    if not clip_paths:
        raise RuntimeError("clips/ にwavファイルがありません。先にdownload_from_drive.pyを実行してください。")

    clips = [AudioSegment.from_wav(p) for p in clip_paths]
    print(f"{len(clips)}個のクリップを読み込みました。")

    # 曲順が毎回同じにならないようシャッフル
    random.shuffle(clips)

    bgm = clips[0]
    i = 1
    while len(bgm) < TARGET_MS:
        next_clip = clips[i % len(clips)]
        # クロスフェード長がクリップ長を超えないように調整
        fade = min(CROSSFADE_MS, len(next_clip) - 100, len(bgm) - 100)
        fade = max(fade, 0)
        bgm = bgm.append(next_clip, crossfade=fade)
        i += 1

    bgm = bgm[:TARGET_MS]
    bgm.export(OUTPUT_FILE, format="mp3", bitrate="192k")

    print(f"完成: {OUTPUT_FILE} (長さ: {len(bgm) / 1000 / 60:.1f}分)")


if __name__ == "__main__":
    main()
