# カフェBGM自動生成 → 自動YouTube投稿

無料構成(MusicGen on Colab + GitHub Actions)による、週1回の完全自動投稿システム。

## 全体の流れ

1. **[手動・週1回] Colabで `musicgen_colab.ipynb` を実行**
   MusicGenで短いBGMを複数生成し、Google Driveの `bgm_clips/latest` に保存する。
2. **[自動] GitHub Actionsが週1回起動**
   Driveからクリップを取得 → 1時間に連結 → 動画化 → YouTubeにアップロード。

手動で残るのは「週1回、Colabのセルを上から実行する」作業だけです(数分)。

## セットアップ手順

### 1. このフォルダをGitHubリポジトリにする
```bash
git init
git add .
git commit -m "init"
git remote add origin <あなたのリポジトリURL>
git push -u origin main
```

### 2. Google Drive用サービスアカウントを作る
1. [Google Cloud Console](https://console.cloud.google.com/) で新規プロジェクト作成
2. 「APIとサービス」→ Google Drive API を有効化
3. 「認証情報」→ サービスアカウントを作成 → JSONキーをダウンロード
4. Google Driveで `bgm_clips` フォルダを作成し、サービスアカウントのメールアドレス
   (`xxxxx@xxxxx.iam.gserviceaccount.com`)に「閲覧者」として共有
5. ダウンロードしたJSONファイルの中身を、GitHubリポジトリの
   Settings → Secrets and variables → Actions → `GDRIVE_SERVICE_ACCOUNT_JSON` に登録

### 3. YouTube API用のOAuth認証情報を作る
1. 同じCloud Consoleプロジェクトで YouTube Data API v3 を有効化
2. 「認証情報」→ OAuthクライアントID(デスクトップアプリ)を作成 → `client_secret.json` をダウンロード
3. `client_secret.json` をこのフォルダに置き、**Colab上で1回だけ** `get_refresh_token.py` を実行
   (`pip install google-auth-oauthlib` してから実行)
4. 表示された `YT_CLIENT_ID` / `YT_CLIENT_SECRET` / `YT_REFRESH_TOKEN` を
   GitHub Secretsにそれぞれ登録

### 4. 背景画像を用意
`assets/background.jpg` にカフェ風の画像を1枚置く(著作権フリー画像推奨)。

### 5. 動作確認
GitHubリポジトリの Actions タブ → `Weekly BGM Upload` → `Run workflow` で
手動実行し、エラーなく動画がアップロードされるか確認する。

## ファイル構成
```
.
├── musicgen_colab.ipynb     # Colabで週1回手動実行(音楽生成)
├── download_from_drive.py   # Driveからクリップ取得
├── combine_bgm.py           # クロスフェード連結
├── make_video.py            # 画像+音声→mp4
├── upload_youtube.py        # YouTube自動投稿
├── get_refresh_token.py     # 初回セットアップ専用
├── requirements.txt
├── assets/background.jpg    # ← 自分で用意
└── .github/workflows/
    └── weekly-upload.yml    # 週1回の自動実行
```

## 注意点
- MusicGenの生成物はオープンソースモデルによる自前生成のため、ライセンス面は比較的クリア。念のため利用モデルのライセンス条項は確認してください。
- GitHub Actionsの無料枠はPublicリポジトリなら実質無制限、Privateなら月2,000分。この構成なら週1回・数分の実行なので十分収まります。
- YouTube Data APIには1日あたりのクォータ制限がありますが、週1回の投稿であれば問題ありません。
