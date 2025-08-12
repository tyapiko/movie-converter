# 🎬 ショート動画コンバーター

YouTubeショート向けの縦型動画（9:16）に変換し、テロップや音声合成を追加できる総合動画編集ツールです。

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-%23FE4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)

## ✨ 主要機能

### 🎥 ショート動画変換
- **フォーマット変換**: 1080x1920（9:16）への自動リサイズ
- **動画トリミング**: 開始・終了時間の指定
- **拡大倍率調整**: 0.5～5.0倍のズーム機能
- **高画質出力**: H.264コーデック、8000k bitrate

### 📝 テロップ機能
- **日本語対応**: NotoSansフォント使用
- **時間指定**: 表示開始・終了時間の設定
- **位置調整**: 上部・中央・下部の配置
- **カラー設定**: 9色のフォントカラー

### 🎤 音声合成（VOICEVOX）
- **雨晴はう**: AIボイスによる読み上げ
- **複数音声**: 時間差での音声追加
- **音量調整**: 個別音量コントロール

### 🎵 BGM機能
- **ループ再生**: 動画長に合わせた自動ループ
- **音量バランス**: BGMと元音声の音量調整
- **対応形式**: MP3, WAV, AAC, M4A, OGG

### 🔗 動画結合
- **複数動画**: 任意の数の動画を結合
- **異なる解像度**: 自動調整機能

## 🚀 クイックスタート（Docker推奨）

### 前提条件
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) がインストールされていること
  - **Windows**: Docker Desktop for Windows
  - **Mac**: Docker Desktop for Mac  
  - **Linux**: Docker Engine + Docker Compose
- Git がインストールされていること

### 1. リポジトリのクローン
```bash
git clone https://github.com/tyapiko/movie-converter.git
cd movie-converter
```

### 2. ワンコマンド起動
```bash
docker-compose up -d
```

### 3. アプリにアクセス
ブラウザで [http://localhost:8501](http://localhost:8501) を開く

### 4. 停止
```bash
docker-compose down
```

## 💻 Windows Desktop での実行手順

### 前提条件の確認
1. **Docker Desktop** がインストール済みで起動していること
2. **Git** がインストールされていること（[Git for Windows](https://git-scm.com/download/win)）

### ステップバイステップ手順

#### 1. Git Bash または PowerShell を開く
```powershell
# PowerShellの場合
# Git Bashの場合も同様のコマンド
```

#### 2. プロジェクトをクローン
```bash
git clone https://github.com/tyapiko/movie-converter.git
cd movie-converter
```

#### 3. Docker Desktopが起動していることを確認
```bash
docker --version
docker-compose --version
```

#### 4. アプリケーションを起動
```bash
docker-compose up -d
```

#### 5. ブラウザでアクセス
- **URL**: http://localhost:8501
- **Chrome、Edge、Firefox** などのモダンブラウザで開く

#### 6. 使用完了後の停止
```bash
# 停止
docker-compose down

# 完全にクリーンアップ（必要時）
docker-compose down --volumes --rmi all
```

### 🔧 Windowsでのトラブルシューティング

#### よくある問題と解決法

**1. Docker Desktopが起動しない**
- Windows の「サービス」で Docker Desktop Service が実行中か確認
- 管理者権限で Docker Desktop を再起動

**2. ポート8501が使用中**
```bash
# 使用中のプロセスを確認
netstat -ano | findstr :8501

# 別のポートを使用する場合
docker-compose up -d --env STREAMLIT_PORT=8502
```

**3. Git clone でエラー**
```bash
# HTTPS接続でエラーの場合
git config --global http.sslVerify false
git clone https://github.com/tyapiko/movie-converter.git
```

**4. メモリ不足エラー**
- Docker Desktop の設定で **メモリを4GB以上** に設定
- **Settings** → **Resources** → **Memory**

## 🛠️ 開発環境セットアップ

### 開発用起動（ホットリロード対応）
```bash
# 開発用docker-compose使用
docker-compose -f docker-compose.dev.yml up -d

# または従来のローカル開発
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### 環境変数設定
```bash
# 環境変数ファイルをコピー
cp .env.example .env

# 必要に応じて.envを編集
nano .env
```

## 📁 プロジェクト構成

```
movie/
├── app.py                      # メインアプリケーション
├── Dockerfile                  # 本番用Docker設定
├── Dockerfile.dev             # 開発用Docker設定
├── docker-compose.yml         # 本番用Docker Compose
├── docker-compose.dev.yml     # 開発用Docker Compose
├── requirements.txt           # Python依存関係
├── .env.example              # 環境変数テンプレート
├── .gitignore               # Git除外設定
├── fonts/                   # フォントファイル
│   └── NotoSansJP-Regular.ttf
├── tmp/                     # 一時ファイル（自動生成）
└── README.md               # このファイル
```

## 📋 対応フォーマット

| 種類 | 入力形式 | 出力形式 |
|------|----------|----------|
| **動画** | MP4, AVI, MOV, MKV | MP4 (H.264) |
| **音声** | MP3, WAV, AAC, M4A, OGG | AAC |

## 🎯 YouTubeショート仕様

| 項目 | 仕様 |
|------|------|
| **解像度** | 1080x1920 (9:16) |
| **最大時間** | 60秒推奨 |
| **ビットレート** | 8000k |
| **コーデック** | H.264 + AAC |

## 📖 使用方法

### ショート動画変換
1. **動画アップロード**: 対応形式の動画ファイルを選択
2. **トリミング設定**: 必要に応じて開始・終了時間を指定
3. **拡大倍率調整**: ズーム効果の設定
4. **テロップ追加**: テキスト、位置、時間、色を設定
5. **音声追加**: VOICEVOX音声の追加
6. **BGM設定**: 背景音楽のアップロードと音量調整
7. **変換実行**: 「ショート動画に変換」ボタンをクリック
8. **ダウンロード**: 完成した動画をダウンロード

### 動画結合
1. **複数選択**: 結合したい動画ファイルを複数選択
2. **順序確認**: 選択順序で結合されることを確認
3. **結合実行**: 「動画を結合」ボタンをクリック
4. **ダウンロード**: 結合された動画をダウンロード

## 🔧 トラブルシューティング

### よくある問題

#### 1. VOICEVOXが動作しない
```bash
# Docker Composeでコンテナ状況確認
docker-compose ps

# VOICEVOXコンテナのログ確認
docker-compose logs voicevox

# コンテナ再起動
docker-compose restart voicevox
```

#### 2. 動画変換が失敗する
- **大きすぎるファイル**: 500MB以下のファイルを使用
- **対応していない形式**: 対応形式を確認
- **メモリ不足**: Dockerのメモリ制限を確認

#### 3. フォントが表示されない
```bash
# フォントファイルの確認
ls -la fonts/
ls -la NotoSansCJK-Regular.ttc

# コンテナ内フォント確認
docker-compose exec app fc-list | grep -i noto
```

#### 4. ポートが使用中
```bash
# ポート使用状況確認
lsof -i :8501
lsof -i :50021

# 別のポートを使用
docker-compose up -d --env STREAMLIT_PORT=8502
```

### ログの確認
```bash
# アプリケーションログ
docker-compose logs app

# VOICEVOX ログ
docker-compose logs voicevox

# リアルタイムログ監視
docker-compose logs -f
```

### パフォーマンス最適化
```bash
# Dockerリソース使用量確認
docker stats

# 不要なコンテナ・イメージの削除
docker system prune -a
```

## 🐛 既知の問題

- WSL環境での音声合成に関する制限
- 大容量動画の処理時間
- 一部ブラウザでのダウンロード制限

## 🤝 コントリビューション

1. Forkしてください
2. 機能ブランチを作成してください (`git checkout -b feature/amazing-feature`)
3. 変更をコミットしてください (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュしてください (`git push origin feature/amazing-feature`)
5. Pull Requestを開いてください

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## 🙏 謝辞

- [VOICEVOX](https://voicevox.hiroshiba.jp/) - 音声合成エンジン
- [Streamlit](https://streamlit.io/) - Webアプリフレームワーク
- [MoviePy](https://zulko.github.io/moviepy/) - 動画処理ライブラリ
- [Noto Sans CJK](https://fonts.google.com/noto) - 日本語フォント

## 📞 サポート

問題や質問がある場合は、[Issues](../../issues) を作成してください。