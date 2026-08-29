"""
clips/ 内のwavファイルを「同じ曲を連続で使ってから切り替える」順序で並べ、
クロスフェードで繋いで約1時間のBGM (output/full_bgm.mp3) を作る。

曲の長さが変わっても必ず1時間に届くよう、目標の長さに達するまで
その場で曲を継ぎ足し続ける方式にしている(あらかじめ決めた個数で打ち切らない)。
"""

import os
import random
from pydub import AudioSegment

CLIPS_DIR = "clips"
OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "full_bgm.mp3")

TARGET_MS = 60 * 60 * 1000  # 1時間
CROSSFADE_MS = 6000  # クロスフェード6秒
MIN_REPEAT = 18  # 同じ曲を連続で使う最小回数
MAX_REPEAT = 22  # 同じ曲を連続で使う最大回数
SAFETY_LIMIT = 2000  # 無限ループ防止用の上限(通常はここまで届かない)


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

    indices = list(range(len(clips)))
    last_index = None
    added_count = 0

    # 最初の1曲
    first_index = random.choice(indices)
    bgm = clips[first_index]
    last_index = first_index

    while len(bgm) < TARGET_MS and added_count < SAFETY_LIMIT:
        choices = [i for i in indices if i != last_index] or indices
        chosen = random.choice(choices)
        repeat = random.randint(MIN_REPEAT, MAX_REPEAT)

        for _ in range(repeat):
            if len(bgm) >= TARGET_MS:
                break
            next_clip = clips[chosen]
            fade = min(CROSSFADE_MS, len(next_clip) - 100, len(bgm) - 100)
            fade = max(fade, 0)
            bgm = bgm.append(next_clip, crossfade=fade)
            added_count += 1

        last_index = chosen

    if len(bgm) < TARGET_MS:
        print(f"警告: 目標の1時間に届きませんでした(実際: {len(bgm) / 1000 / 60:.1f}分)。素材を増やすことを検討してください。")

    bgm = bgm[:TARGET_MS] if len(bgm) > TARGET_MS else bgm
    bgm.export(OUTPUT_FILE, format="mp3", bitrate="192k")

    print(f"完成: {OUTPUT_FILE} (長さ: {len(bgm) / 1000 / 60:.1f}分)")


if __name__ == "__main__":
    main()
