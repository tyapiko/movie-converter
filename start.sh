#!/bin/bash

echo "🐳 Starting VOICEVOX Docker container..."
# 既存のコンテナがあれば停止・削除
docker stop voicevox 2>/dev/null || true
docker rm voicevox 2>/dev/null || true

# VOICEVOXコンテナを起動
docker run --rm -d -p 50021:50021 --name voicevox voicevox/voicevox_engine:cpu-ubuntu20.04-latest

echo "⏳ Waiting for VOICEVOX to start..."
sleep 10

echo "🎬 Starting Streamlit app..."
source venv/bin/activate
streamlit run app.py