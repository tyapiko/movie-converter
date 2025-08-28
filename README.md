# YouTube Shorts Video Converter

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://hub.docker.com/)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)

🎬 **包括的なStreamlit動画編集ツール** - 縦型動画変換、動画結合、スライド動画生成を一つのアプリケーションで実現

## 🌟 機能概要

### 1. ショート動画変換 📱
- **9:16フォーマット変換**: 通常の動画をYouTube Shorts形式に自動変換
- **テキストオーバーレイ**: 時間指定でテロップを追加
- **VOICEVOX音声合成**: 日本語テキストの自動読み上げ
- **BGM追加**: 背景音楽の追加と音量調整
- **高品質出力**: H.264エンコードによる最適化

### 2. 動画結合 🔗
- **複数動画統合**: 複数の動画ファイルを順番に結合
- **異なる解像度対応**: 様々な動画形式・解像度を自動調整
- **音声トラック保持**: 全ての音声情報を統合

### 3. スライド動画作成 📊
- **PowerPoint変換**: PPTXファイルから動画を自動生成
- **16:9出力**: プレゼンテーション向け横型フォーマット
- **歌詞同期**: カラオケ風の歌詞表示機能
- **カスタム表示時間**: スライドごとの個別時間設定

## 🏗️ アーキテクチャ

### モジュラー設計（v2.0）
```
src/
├── audio/           # 音声処理（VOICEVOX統合）
│   ├── __init__.py
│   └── voicevox.py  # VOICEVOX クライアント
├── config/          # 設定管理
│   ├── __init__.py
│   └── settings.py  # アプリケーション設定
├── ui/              # UIコンポーネント
│   ├── __init__.py
│   └── components.py # 再利用可能なUI要素
├── utils/           # ユーティリティ関数
│   ├── __init__.py
│   └── file_utils.py # ファイル操作
└── video/           # 動画処理・テキストオーバーレイ
    ├── __init__.py
    ├── processor.py     # 動画処理エンジン
    └── text_overlay.py  # テキスト合成
```

### 技術スタック
- **フロントエンド**: Streamlit (Python Web UI)
- **動画処理**: MoviePy + FFmpeg
- **音声合成**: VOICEVOX Engine
- **画像処理**: PIL (Pillow) + OpenCV
- **コンテナ**: Docker + Docker Compose
- **フォント**: Noto Sans CJK (日本語サポート)

## 🚀 クイックスタート

### 前提条件
- Docker & Docker Compose
- 4GB以上のRAM
- 10GB以上の空きストレージ

### インストールと起動

```bash
# リポジトリをクローン
git clone <repository-url>
cd movie

# 開発環境で起動（ホットリロード有効）
docker-compose -f docker-compose.dev.yml up -d

# または本番環境で起動
docker-compose up -d

# ブラウザでアクセス
open http://localhost:8501
```

### 基本的な使用方法

1. **ツール選択**: サイドバーから使用したい機能を選択
2. **ファイルアップロード**: 対応する形式のファイルをドラッグ&ドロップ
3. **設定調整**: 各種パラメータをカスタマイズ
4. **処理実行**: 変換ボタンをクリック
5. **結果ダウンロード**: 処理完了後にファイルをダウンロード

## 📋 対応形式

### 入力対応形式

| カテゴリ | 対応形式 |
|----------|----------|
| 動画 | MP4, AVI, MOV, MKV |
| 音声 | MP3, WAV, AAC, M4A, OGG |
| プレゼンテーション | PPTX, PPT |

### 出力形式
- **動画**: MP4 (H.264 + AAC)
- **解像度**: 
  - ショート動画: 1080×1920 (9:16)
  - スライド動画: 1920×1080 (16:9)

## ⚙️ 設定とカスタマイズ

### 環境変数
```bash
# VOICEVOX接続URL（自動検出）
VOICEVOX_URL=http://voicevox:50021

# 一時ファイル保存先
TEMP_DIR=/app/tmp
```

### パフォーマンスチューニング
- **メモリ使用量**: 大容量ファイル処理時は8GB推奨
- **CPU使用**: マルチコア環境で最適化
- **ストレージ**: SSDでの高速処理

## 🛠️ 開発者向け情報

### プロジェクト構造
```
movie/
├── src/                    # モジュラーコード
│   ├── audio/             # 音声処理
│   ├── config/            # 設定管理
│   ├── ui/                # UIコンポーネント
│   ├── utils/             # ユーティリティ
│   └── video/             # 動画処理
├── app_new.py             # リファクタリング版メイン
├── app.py                 # レガシー版（互換性維持）
├── docker-compose.yml     # 本番環境
├── docker-compose.dev.yml # 開発環境
├── requirements.txt       # Python依存関係
└── fonts/                 # 日本語フォント
```

### 開発コマンド

```bash
# 開発環境起動（ホットリロード）
docker-compose -f docker-compose.dev.yml up -d

# ログ確認
docker-compose logs -f app

# コンテナ内シェルアクセス
docker-compose exec app bash

# テスト実行
python test_basic.py

# コード品質チェック
ruff check src/
black src/
```

### 新機能追加手順

1. **モジュール作成**: 適切な`src/`サブディレクトリに機能を実装
2. **UIコンポーネント**: `src/ui/components.py`に再利用可能なUI要素を追加
3. **設定追加**: `src/config/settings.py`で新しい設定項目を定義
4. **統合**: `app_new.py`でメインアプリケーションに統合
5. **テスト**: 基本テストとユーザビリティテストを実施

## 🧪 テスト

### 自動テスト
```bash
# 基本ヘルスチェック
python test_basic.py

# または
bash run_tests.sh
```

### 手動テスト項目
- [ ] 各ツールの基本動作
- [ ] ファイルアップロード・ダウンロード
- [ ] エラーハンドリング
- [ ] 大容量ファイル処理
- [ ] VOICEVOX連携

## 🔧 トラブルシューティング

### よくある問題

**VOICEVOX接続エラー**
```bash
# VOICEVOXコンテナ状況確認
docker-compose ps voicevox
docker-compose logs voicevox

# 手動接続テスト
curl http://localhost:50021/speakers
```

**メモリ不足エラー**
```bash
# Docker メモリ上限を増加
# Docker Desktop > Settings > Resources > Memory
```

**フォント表示問題**
```bash
# コンテナ内フォント確認
docker-compose exec app ls -la /app/fonts/
```

**ポート競合**
```bash
# 別ポートで起動
docker-compose up -d -e PORT=8502
```

## 📈 パフォーマンス指標

### 処理時間目安

| 操作 | ファイルサイズ | 処理時間 |
|------|---------------|----------|
| ショート変換 | 100MB | 1-3分 |
| 動画結合 | 500MB | 3-8分 |
| スライド生成 | 20スライド | 2-5分 |

### システム要件

| 項目 | 最小要件 | 推奨要件 |
|------|----------|----------|
| RAM | 4GB | 8GB+ |
| CPU | 2コア | 4コア+ |
| ストレージ | 10GB | 50GB+ |

## 🤝 コントリビューション

### 開発参加方法

1. **フォーク**: このリポジトリをフォーク
2. **ブランチ**: `git checkout -b feature/新機能名`
3. **実装**: モジュラーアーキテクチャに従って開発
4. **テスト**: 自動テスト＋手動テストを実施
5. **プルリクエスト**: 詳細な説明と共に提出

### コーディング規約
- **Python**: PEP 8 + Black フォーマッタ
- **モジュール**: 単一責任原則に従った分割
- **ドキュメント**: 関数・クラスにdocstring必須
- **エラーハンドリング**: 例外処理とユーザーフレンドリーメッセージ

## 📚 バージョン履歴

### v2.0.0 (2025-08-28)
- **リファクタリング**: モジュラーアーキテクチャに全面改修
- **UI改善**: サイドバーの簡素化とページ機能追加
- **保守性向上**: コードの分割と再利用性の向上
- **テスト強化**: 自動テストとエラーハンドリングの改善

### v1.0.0 (初期版)
- 基本的なショート動画変換機能
- VOICEVOX音声合成統合
- 動画結合機能
- スライド動画生成機能

## 📄 ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照

## 🙏 謝辞

- **VOICEVOX**: 高品質日本語音声合成エンジン
- **MoviePy**: Python動画処理ライブラリ
- **Streamlit**: 高速Webアプリケーション開発フレームワーク
- **FFmpeg**: 包括的動画処理ツール

---

**プロジェクト作成者**: AI Assistant  
**最終更新**: 2025年8月28日  
**バージョン**: 2.0.0（リファクタリング版）