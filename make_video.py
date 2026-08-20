"""
output/full_bgm.mp3 と assets/background.jpg から
output/video.mp4 を作る(ffmpegを呼び出すだけの薄いラッパー)。

background.jpg はリポジトリの assets/ フォルダに好きな画像を1枚置いておく。
"""

import subprocess
import os

AUDIO_FILE = "output/full_bgm.mp3"
IMAGE_FILE = "assets/background.jpg"
VIDEO_FILE = "output/video.mp4"


def main():
    if not os.path.exists(AUDIO_FILE):
        raise FileNotFoundError(f"{AUDIO_FILE} がありません。先にcombine_bgm.pyを実行してください。")
    if not os.path.exists(IMAGE_FILE):
        raise FileNotFoundError(
            f"{IMAGE_FILE} がありません。assets/background.jpg を用意してください。"
        )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", IMAGE_FILE,
        "-i", AUDIO_FILE,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        VIDEO_FILE,
    ]
    subprocess.run(cmd, check=True)
    print(f"完成: {VIDEO_FILE}")


if __name__ == "__main__":
    main()
