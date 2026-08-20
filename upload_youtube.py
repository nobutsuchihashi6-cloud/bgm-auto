"""
output/video.mp4 をYouTubeにアップロードする。

事前準備(初回のみ、手元のPCやColabで1回だけ実施):
1. Google Cloud ConsoleでOAuthクライアントID(デスクトップアプリ)を作成
2. google-auth-oauthlibで一度だけ認証フローを回し、refresh_tokenを取得
3. 以下をGitHub Secretsに登録:
   - YT_CLIENT_ID
   - YT_CLIENT_SECRET
   - YT_REFRESH_TOKEN
"""

import os
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

VIDEO_FILE = "output/video.mp4"


def get_youtube_service():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"],
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    return build("youtube", "v3", credentials=creds)


def main():
    if not os.path.exists(VIDEO_FILE):
        raise FileNotFoundError(f"{VIDEO_FILE} がありません。先にmake_video.pyを実行してください。")

    today = datetime.date.today().strftime("%Y/%m/%d")

    title = f"Relaxing Cafe Jazz BGM - {today} | 作業用・勉強用1時間"
    description = (
        "カフェで流れているような、落ち着いたジャズBGMです。\n"
        "作業用・読書用・勉強用・リラックスタイムにどうぞ。\n\n"
        "#lofi #cafejazz #bgm"
    )

    youtube = get_youtube_service()

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["lofi", "cafe jazz", "bgm", "relaxing music", "study music"],
                "categoryId": "10",  # Music
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        },
        media_body=MediaFileUpload(VIDEO_FILE, chunksize=-1, resumable=True),
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"アップロード中... {int(status.progress() * 100)}%")

    print(f"アップロード完了: https://youtu.be/{response['id']}")


if __name__ == "__main__":
    main()
