"""
clips/ 内のwavファイルを「同じ曲を2〜3回連続で使ってから切り替える」順序で並べ、
クロスフェードで繋いで約1時間のBGM (output/full_bgm.mp3) を作る。

単純に毎回別の曲へ切り替えるより、同じ曲がある程度連続する方が
「頻繁に切り替わって落ち着かない」印象を減らせる。
"""

import os
import random
from pydub import AudioSegment

CLIPS_DIR = "clips"
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "full_bgm.mp3")

TARGET_MS = 60 * 60 * 1000  # 1時間
CROSSFADE_MS = 6000  # クロスフェード6秒
MIN_REPEAT = 2  # 同じ曲を連続で使う最小回数
MAX_REPEAT = 3  # 同じ曲を連続で使う最大回数


def build_play_order(num_clips):
    order = []
    last_index = None
    indices = list(range(num_clips))

    while True:
        choices = [i for i in indices if i != last_index] or indices
        chosen = random.choice(choices)
        repeat = random.randint(MIN_REPEAT, MAX_REPEAT)
        order.extend([chosen] * repeat)
        last_index = chosen

        if len(order) > 200:
            break

    return order


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

    play_order = build_play_order(len(clips))

    bgm = clips[play_order[0]]
    for idx in play_order[1:]:
        if len(bgm) >= TARGET_MS:
            break
        next_clip = clips[idx]
        fade = min(CROSSFADE_MS, len(next_clip) - 100, len(bgm) - 100)
        fade = max(fade, 0)
        bgm = bgm.append(next_clip, crossfade=fade)

    bgm = bgm[:TARGET_MS]
    bgm.export(OUTPUT_FILE, format="mp3", bitrate="192k")

    print(f"完成: {OUTPUT_FILE} (長さ: {len(bgm) / 1000 / 60:.1f}分)")


if __name__ == "__main__":
    main()
