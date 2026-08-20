"""
【初回セットアップ専用・1回だけ実行】

YouTube Data APIのrefresh_tokenを取得するためのスクリプト。
PCがない場合はGoogle ColabやGitHub Codespacesなど、ブラウザ操作ができる
クラウド環境で実行してください(このスクリプトはローカルサーバーを立てず、
手動でコードを貼り付ける方式にしてあります)。

事前準備:
1. Google Cloud Console (https://console.cloud.google.com/) でプロジェクトを作成
2. 「APIとサービス」→ YouTube Data API v3 を有効化
3. 「認証情報」→ OAuthクライアントIDを作成(アプリケーションの種類: デスクトップアプリ)
4. ダウンロードしたclient_secret.jsonをこのスクリプトと同じフォルダに置く

実行すると表示されるURLをブラウザで開き、許可した後に表示される
認証コードをターミナルに貼り付けてください。
最後に表示される refresh_token をGitHub Secretsの YT_REFRESH_TOKEN に登録します。
"""

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRET_FILE = "client_secret.json"


def main():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_console()  # ブラウザURL表示 → コード手動貼り付け方式

    print("\n=== 以下をGitHub Secretsに登録してください ===")
    print(f"YT_CLIENT_ID={creds.client_id}")
    print(f"YT_CLIENT_SECRET={creds.client_secret}")
    print(f"YT_REFRESH_TOKEN={creds.refresh_token}")


if __name__ == "__main__":
    main()
