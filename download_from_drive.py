"""
Google Driveの 'bgm_clips' フォルダの中から、
まだ使っていない一番古い日付フォルダを1つ選んでダウンロードする。
ダウンロードが終わったら、そのフォルダを 'bgm_clips/used' に移動して
「使用済み」の印をつける(次回以降、同じ音楽が再利用されないようにするため)。

これにより、Colabで複数週分の音楽をまとめて作りだめしておくことができる。
GitHub Actionsは実行されるたびに、未使用の中から一番古いものを1つずつ消費していく。
"""

import os
import io
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

DOWNLOAD_DIR = "clips"
USED_FOLDER_NAME = "used"
LATEST_FOLDER_NAME = "latest"


def get_drive_service():
    creds_json = os.environ["GDRIVE_SERVICE_ACCOUNT_JSON"]
    creds_info = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(
        creds_info, scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=creds)


def find_folder_id(service, name, parent_id=None):
    query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    if not files:
        return None
    return files[0]["id"]


def get_or_create_folder(service, name, parent_id):
    existing = find_folder_id(service, name, parent_id=parent_id)
    if existing:
        return existing
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def list_subfolders(service, parent_id):
    query = (
        f"'{parent_id}' in parents and trashed = false "
        f"and mimeType = 'application/vnd.google-apps.folder'"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    return results.get("files", [])


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


def move_folder(service, folder_id, new_parent_id, old_parent_id):
    service.files().update(
        fileId=folder_id,
        addParents=new_parent_id,
        removeParents=old_parent_id,
        fields="id, parents",
    ).execute()


def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    service = get_drive_service()

    bgm_clips_id = find_folder_id(service, "bgm_clips")
    if not bgm_clips_id:
        raise FileNotFoundError("bgm_clips フォルダが見つかりません。")

    used_id = get_or_create_folder(service, USED_FOLDER_NAME, parent_id=bgm_clips_id)

    subfolders = list_subfolders(service, bgm_clips_id)
    candidates = [
        f for f in subfolders
        if f["name"] not in (USED_FOLDER_NAME, LATEST_FOLDER_NAME)
    ]
    candidates.sort(key=lambda f: f["name"])

    if not candidates:
        raise RuntimeError(
            "未使用の音楽フォルダが見つかりません。Colabで新しく生成してください。"
        )

    target = candidates[0]
    target_id = target["id"]
    print(f"使用するフォルダ: {target['name']}")

    files = list_files_in_folder(service, target_id)
    wav_files = [f for f in files if f["name"].endswith(".wav")]

    if not wav_files:
        raise RuntimeError(f"{target['name']} フォルダにwavファイルがありません。")

    for f in wav_files:
        dest = os.path.join(DOWNLOAD_DIR, f["name"])
        print(f"ダウンロード中: {f['name']}")
        download_file(service, f["id"], dest)

    move_folder(service, target_id, new_parent_id=used_id, old_parent_id=bgm_clips_id)
    print(f"'{target['name']}' を使用済みとしてマークしました。")

    print(f"完了。{len(wav_files)}個のクリップを {DOWNLOAD_DIR}/ に保存しました。")


if __name__ == "__main__":
    main()
