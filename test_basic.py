#!/usr/bin/env python3
"""
基本的な自動テストスクリプト
使用方法: python test_basic.py
"""

import subprocess
import time
import requests
import sys
import os

def run_command(cmd, timeout=30):
    """コマンドを実行して結果を返す"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"

def test_docker_compose():
    """Docker Composeの起動テスト"""
    print("🔧 Docker Compose起動テスト...")
    
    # 停止して再起動
    run_command("docker-compose down")
    success, stdout, stderr = run_command("docker-compose up -d", timeout=120)
    
    if not success:
        print(f"❌ Docker Compose起動失敗: {stderr}")
        return False
    
    print("✅ Docker Compose起動成功")
    return True

def test_app_health():
    """アプリケーションのヘルスチェック"""
    print("🏥 アプリケーションヘルスチェック...")
    
    # 60秒間リトライ
    for i in range(30):
        try:
            response = requests.get("http://localhost:8501/_stcore/health", timeout=5)
            if response.status_code == 200:
                print("✅ アプリケーション正常起動")
                return True
        except:
            pass
        
        time.sleep(2)
        print(f"⏳ 待機中... {i+1}/30")
    
    print("❌ アプリケーション起動失敗")
    return False

def test_voicevox_connection():
    """VOICEVOX接続テスト"""
    print("🎤 VOICEVOX接続テスト...")
    
    try:
        # VOICEVOXコンテナの状態確認
        success, stdout, stderr = run_command("docker-compose ps | grep voicevox")
        if "Up" not in stdout:
            print("⚠️ VOICEVOXコンテナが起動していません")
            return False
        
        # VOICEVOX API確認
        response = requests.get("http://localhost:50021/speakers", timeout=10)
        if response.status_code == 200:
            print("✅ VOICEVOX接続成功")
            return True
        else:
            print(f"⚠️ VOICEVOX応答異常: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️ VOICEVOX接続失敗: {e}")
        return False

def test_basic_functionality():
    """基本機能のテスト"""
    print("🧪 基本機能テスト...")
    
    try:
        # Streamlitアプリのメインページを確認
        response = requests.get("http://localhost:8501", timeout=10)
        if response.status_code == 200 and "ショート動画コンバーター" in response.text:
            print("✅ メインページ正常表示")
            return True
        else:
            print("❌ メインページ表示異常")
            return False
    except Exception as e:
        print(f"❌ 基本機能テスト失敗: {e}")
        return False

def cleanup():
    """テスト後のクリーンアップ"""
    print("🧹 クリーンアップ...")
    run_command("docker-compose down")

def main():
    """メインテスト実行"""
    print("🚀 自動テスト開始")
    print("=" * 50)
    
    tests = [
        ("Docker Compose", test_docker_compose),
        ("App Health", test_app_health),
        ("VOICEVOX Connection", test_voicevox_connection),
        ("Basic Functionality", test_basic_functionality),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} でエラー: {e}")
            results.append((test_name, False))
        print()
    
    # 結果サマリー
    print("📊 テスト結果サマリー")
    print("=" * 50)
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 結果: {passed}/{len(results)} テスト通過")
    
    # クリーンアップ
    cleanup()
    
    # 終了コード
    sys.exit(0 if passed == len(results) else 1)

if __name__ == "__main__":
    main()