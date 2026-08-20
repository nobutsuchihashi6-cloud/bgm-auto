"""
Google Driveの 'bgm_clips/latest' フォルダから、
Colabで生成したwavクリップをすべてダウンロードする。

事前準備:
1. Google Cloud Consoleでサービスアカウントを作成し、JSONキーを取得
2. そのサービスアカウントのメールアドレスに、Drive上の bgm_clips フォルダを
   「閲覧者」として共有しておく
3. JSONキーの中身をGitHub Secretsに `GDRIVE_SERVICE_ACCOUNT_JSON` として登録
"""

import os
import io
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

DOWNLOAD_DIR = "clips"
FOLDER_NAME_TARGET = "latest"


def get_drive_service():
    creds_json = os.environ["GDRIVE_SERVICE_ACCOUNT_JSON"]
    creds_info = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(
        creds_info, scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build("drive", "v3", credentials=creds)


def find_folder_id(service, name, parent_id=None):
    query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    if not files:
        raise FileNotFoundError(f"フォルダが見つかりません: {name}")
    return files[0]["id"]


def list_files_in_folder(service, folder_id):
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    return results.get("files", [])


def download_file(service, file_id, dest_path):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(dest_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()


def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    service = get_drive_service()

    bgm_clips_id = find_folder_id(service, "bgm_clips")
    latest_id = find_folder_id(service, FOLDER_NAME_TARGET, parent_id=bgm_clips_id)

    files = list_files_in_folder(service, latest_id)
    wav_files = [f for f in files if f["name"].endswith(".wav")]

    if not wav_files:
        raise RuntimeError("latest フォルダにwavファイルがありません。Colabでの生成を確認してください。")

    for f in wav_files:
        dest = os.path.join(DOWNLOAD_DIR, f["name"])
        print(f"ダウンロード中: {f['name']}")
        download_file(service, f["id"], dest)

    print(f"完了。{len(wav_files)}個のクリップを {DOWNLOAD_DIR}/ に保存しました。")


if __name__ == "__main__":
    main()
