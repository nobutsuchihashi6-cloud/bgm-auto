"""
output/full_bgm.mp3 と、リポジトリ内にある背景写真(複数)から
output/video.mp4 を作る(ffmpegを呼び出すだけの薄いラッパー)。

背景写真は、リポジトリのルート直下に IMG_*.jpeg / IMG_*.jpg / *.png のような
形で置かれている想定。実行するたびにランダムで1枚選ぶ。
"""

import subprocess
import os
import glob
import random

AUDIO_FILE = "output/full_bgm.mp3"
VIDEO_FILE = "output/video.mp4"

# 探す場所:ルート直下と assets 以下、両方に対応
IMAGE_PATTERNS = [
    "*.jpg", "*.jpeg", "*.JPG", "*.JPEG", "*.png", "*.PNG",
    "assets/*.jpg", "assets/*.jpeg", "assets/*.JPG", "assets/*.JPEG", "assets/*.png",
    "assets/backgrounds/*.jpg", "assets/backgrounds/*.jpeg",
    "assets/backgrounds/*.JPG", "assets/backgrounds/*.JPEG", "assets/backgrounds/*.png",
]


def find_background_images():
    found = []
    for pattern in IMAGE_PATTERNS:
        found.extend(glob.glob(pattern))
    # ある程度サイズの大きい画像ファイルのみに絞る(1KB未満は除外)
    found = [f for f in found if os.path.getsize(f) > 1024]
    return sorted(set(found))


def main():
    if not os.path.exists(AUDIO_FILE):
        raise FileNotFoundError(f"{AUDIO_FILE} がありません。先にcombine_bgm.pyを実行してください。")

    images = find_background_images()
    if not images:
        raise FileNotFoundError(
            "背景画像が見つかりません。リポジトリのルート、または assets/ / assets/backgrounds/ に"
            "画像ファイル(jpg/jpeg/png)を置いてください。"
        )

    image_file = random.choice(images)
    print(f"{len(images)}枚の候補から選択: {image_file}")

    os.makedirs("output", exist_ok=True)

        cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-r", "1",
        "-i", image_file,
        "-i", AUDIO_FILE,
        "-vf", "scale=1280:-2",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "stillimage",
        "-crf", "30",
        "-r", "1",
        "-c:a", "aac",
        "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        VIDEO_FILE,
    ]

    subprocess.run(cmd, check=True)
    print(f"完成: {VIDEO_FILE}")


if __name__ == "__main__":
    main()
