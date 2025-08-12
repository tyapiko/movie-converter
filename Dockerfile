# マルチステージビルドを使用して最適化
FROM python:3.11-slim as builder

# システム依存関係をインストール（ビルド用）
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をビルド
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 実行用の軽量イメージ
FROM python:3.11-slim

# システム依存関係をインストール（実行用）
RUN apt-get update && apt-get install -y \
    ffmpeg \
    fonts-noto-cjk \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ビルダーステージからPythonパッケージをコピー
COPY --from=builder /root/.local /root/.local

# パスを更新
ENV PATH=/root/.local/bin:$PATH

# 作業ディレクトリを設定
WORKDIR /app

# アプリケーションファイルをコピー
COPY app.py .
COPY fonts/ fonts/
COPY NotoSansCJK-Regular.ttc .

# Streamlitポートを公開
EXPOSE 8501

# ヘルスチェックを追加
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/healthz || exit 1

# 非rootユーザーを作成
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Streamlitアプリを起動
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]