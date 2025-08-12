# 🔐 セキュリティガイド

## 現在のセキュリティ状況

### ✅ 実装済みのセキュリティ対策

#### Docker セキュリティ
- **非rootユーザー実行**: コンテナ内で `appuser` (UID: 1000) を使用
- **最小権限の原則**: 必要最小限のシステムパッケージのみインストール
- **セキュアベースイメージ**: `python:3.11-slim` を使用
- **ネットワーク分離**: 専用Dockerネットワークで分離

#### アプリケーション セキュリティ
- **一時ファイル管理**: アップロードファイルの適切なクリーンアップ
- **秘密情報の保護**: ハードコードされた認証情報なし

### ⚠️ 改善が必要なセキュリティ事項

## 重要度: 🔴 高 (即座に対応推奨)

### 1. ネットワークバインディング制限

**現在の問題**:
```bash
--server.address=0.0.0.0  # 全インターフェースでリスニング
```

**推奨設定**:
```bash
--server.address=127.0.0.1  # ローカルホストのみ
```

**対応方法**:
```dockerfile
# Dockerfile の CMD を修正
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=127.0.0.1", "--server.headless=true"]
```

### 2. リバースプロキシの使用

**本番環境での推奨構成**:
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
  
  app:
    build: .
    expose:
      - "8501"  # ポート公開を内部のみに限定
    # ports を削除してセキュリティ向上
```

## 重要度: 🟡 中 (計画的対応推奨)

### 3. ファイルアップロード制限

**推奨設定**:
```python
# app.py に追加
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
ALLOWED_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.mp3', '.wav', '.aac'}

def validate_uploaded_file(file):
    if file.size > MAX_FILE_SIZE:
        raise ValueError("ファイルサイズが大きすぎます")
    
    file_ext = os.path.splitext(file.name)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValueError("サポートされていないファイル形式です")
```

### 4. レート制限の実装

**nginx設定例**:
```nginx
# nginx.conf
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;
    
    server {
        location / {
            limit_req zone=api burst=5 nodelay;
            proxy_pass http://app:8501;
        }
    }
}
```

### 5. セッション管理強化

**推奨設定**:
```python
# .streamlit/config.toml
[server]
sessionTimeout = 1800  # 30分
enableCORS = false
enableXsrfProtection = true
```

## 重要度: 🟢 低 (時間があるときに対応)

### 6. セキュリティヘッダー追加

**nginx設定例**:
```nginx
server {
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    add_header Content-Security-Policy "default-src 'self'";
}
```

### 7. ログ設定の改善

**推奨設定**:
```python
import logging

# 機密情報のマスキング
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/app.log'),
        logging.StreamHandler()
    ]
)

# 機密情報をログから除外
def sanitize_log(message):
    # パスワード、トークンなどをマスキング
    return re.sub(r'(password|token|key)=[^&\s]*', r'\1=***', message)
```

## 🚀 本番環境向けセキュリティチェックリスト

### 必須対応事項
- [ ] **SSL/TLS証明書** の設定
- [ ] **リバースプロキシ** (nginx/Apache) の導入
- [ ] **ファイアウォール** の設定
- [ ] **定期的なセキュリティ更新**
- [ ] **バックアップ戦略** の策定

### 推奨対応事項
- [ ] **WAF** (Web Application Firewall) の導入
- [ ] **侵入検知システム** の設定
- [ ] **セキュリティ監査ログ** の有効化
- [ ] **コンテナスキャン** の自動化
- [ ] **依存関係の脆弱性チェック**

## 🔍 セキュリティ監査コマンド

### Dockerセキュリティチェック
```bash
# コンテナのセキュリティスキャン
docker scout cves movie-app:latest

# 実行中プロセスの確認
docker exec movie-converter-app ps aux

# ネットワーク設定の確認
docker network inspect movie-converter-network
```

### 依存関係のセキュリティチェック
```bash
# Python依存関係の脆弱性チェック
pip-audit

# システムパッケージの更新確認
docker exec movie-converter-app apt list --upgradable
```

## 📞 セキュリティインシデント対応

### 緊急時の対応手順
1. **即座にサービス停止**: `docker-compose down`
2. **ログの保全**: `docker-compose logs > incident_$(date).log`
3. **ネットワーク分離**: ファイアウォールルールの更新
4. **影響範囲の調査**: アクセスログとエラーログの分析
5. **修正とテスト**: 脆弱性の修正とセキュリティテスト
6. **段階的復旧**: 限定的なサービス再開

## 🛡️ 継続的セキュリティ対策

### 定期実施項目
- **月次**: 依存関係の更新とセキュリティパッチ適用
- **四半期**: セキュリティ監査とペネトレーションテスト
- **半年**: セキュリティ設定の見直しとポリシー更新

---

**注意**: このアプリケーションは教育・開発目的で作成されています。本番環境での使用前には、組織のセキュリティポリシーに従って追加の対策を実施してください。