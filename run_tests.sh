#!/bin/bash
# 簡単テスト実行スクリプト

echo "🚀 ショート動画コンバーター テスト開始"
echo "=================================="

# Python環境確認
if command -v python3 &> /dev/null; then
    echo "✅ Python3 検出"
    python3 test_basic.py
else
    echo "❌ Python3 が見つかりません"
    echo "手動でテストを実行します..."
    
    # 手動テスト
    echo "🔧 Docker Compose 起動..."
    docker-compose up -d
    
    echo "⏳ サービス待機..."
    sleep 30
    
    echo "🧪 テスト実行..."
    
    # ヘルスチェック
    if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        echo "✅ アプリケーション OK"
    else
        echo "❌ アプリケーション エラー"
    fi
    
    # VOICEVOX チェック
    if curl -f http://localhost:50021/speakers > /dev/null 2>&1; then
        echo "✅ VOICEVOX OK"
    else
        echo "⚠️ VOICEVOX エラー（オプション機能）"
    fi
    
    echo "🧹 クリーンアップ..."
    docker-compose down
fi

echo "テスト完了 🎉"