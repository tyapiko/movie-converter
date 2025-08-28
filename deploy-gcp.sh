#!/bin/bash

# GCP Cloud Run デプロイスクリプト
set -e

# 色付きの出力用関数
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
echo_success() { echo -e "${GREEN}✅ $1${NC}"; }
echo_error() { echo -e "${RED}❌ $1${NC}"; }

# 設定
PROJECT_ID="${1:-}"
REGION="${2:-asia-northeast1}"
SERVICE_NAME="movie-converter"
BUCKET_NAME="movie-converter-files-$PROJECT_ID"

if [ -z "$PROJECT_ID" ]; then
    echo_error "使用方法: $0 <GCP_PROJECT_ID> [REGION]"
    echo "例: $0 my-project-12345 asia-northeast1"
    exit 1
fi

echo_info "=== YouTube Shorts Video Converter - GCP デプロイ ==="
echo_info "プロジェクト: $PROJECT_ID"
echo_info "リージョン: $REGION"
echo_info "サービス名: $SERVICE_NAME"
echo ""

# 前提条件の確認
echo_info "前提条件を確認中..."

if ! command -v gcloud &> /dev/null; then
    echo_error "Google Cloud CLI (gcloud) がインストールされていません"
    echo "インストール方法: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo_error "Docker がインストールされていません"
    exit 1
fi

# Google Cloud プロジェクトの設定
echo_info "Google Cloud プロジェクトを設定中..."
gcloud config set project $PROJECT_ID

# 必要なAPIの有効化
echo_info "必要なAPIを有効化中..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    storage.googleapis.com

# Cloud Storageバケットの作成
echo_info "Cloud Storage バケットを作成中..."
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME/ 2>/dev/null || echo_info "バケットは既に存在します"

# Docker イメージのビルドとプッシュ
echo_info "Docker イメージをビルド中..."
docker build -f Dockerfile.cloudrun -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .

echo_info "Container Registry に イメージをプッシュ中..."
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

# Cloud Run へデプロイ
echo_info "Cloud Run にデプロイ中..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 4Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10 \
    --set-env-vars "GCP_PROJECT_ID=$PROJECT_ID,CLOUD_STORAGE_BUCKET=$BUCKET_NAME" \
    --quiet

# サービスURLを取得
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')

echo ""
echo_success "=== デプロイ完了! ==="
echo_success "サービスURL: $SERVICE_URL"
echo_info "Cloud Storage: gs://$BUCKET_NAME"
echo ""
echo_info "🎉 アプリケーションにアクセスしてテストしてください！"

# 料金見積もりを表示
echo ""
echo_info "=== 概算料金 (月額) ==="
echo_info "Cloud Run (100万リクエスト/月): 約 $12-24"
echo_info "Cloud Storage (10GB): 約 $0.20"
echo_info "Container Registry: 約 $0.10"
echo_info "合計概算: 約 $12-25/月"
echo ""
echo_info "💡 使用量に応じて料金は変動します。詳細は GCP 請求書でご確認ください。"