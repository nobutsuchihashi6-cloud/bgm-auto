"""
output/full_bgm.mp3 と、リポジトリ内にある背景写真(複数)から
output/video.mp4 を作る(ffmpegを呼び出すだけの薄いラッパー)。

直近で使った画像は避けて選ぶことで、体感的な偏りを減らしている。
履歴は本体リポジトリ直下の .last_images.json に保存する。
"""

import subprocess
import os
import glob
import random
import json

AUDIO_FILE = "output/full_bgm.mp3"
VIDEO_FILE = "output/video.mp4"
HISTORY_FILE = ".last_images.json"
HISTORY_SIZE = 2  # 直近何回分の画像を避けるか

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
    found = [f for f in found if os.path.getsize(f) > 1024]
    return sorted(set(found))


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-HISTORY_SIZE:], f)


def choose_image(images):
    history = load_history()
    candidates = [img for img in images if img not in history]
    if not candidates:
        # 全部履歴に入っている(画像が少ない場合)なら、制限を無視して全体から選ぶ
        candidates = images

    chosen = random.choice(candidates)

    history.append(chosen)
    save_history(history)

    return chosen


def main():
    if not os.path.exists(AUDIO_FILE):
        raise FileNotFoundError(f"{AUDIO_FILE} がありません。先にcombine_bgm.pyを実行してください。")

    images = find_background_images()
    if not images:
        raise FileNotFoundError(
            "背景画像が見つかりません。リポジトリのルート、または assets/ / assets/backgrounds/ に"
            "画像ファイル(jpg/jpeg/png)を置いてください。"
        )

    image_file = choose_image(images)
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

