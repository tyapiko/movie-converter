import streamlit as st

st.set_page_config(
    page_title="対応形式",
    page_icon="ℹ️",
    layout="wide"
)

st.title("ℹ️ 対応形式・技術仕様")

# 2列レイアウトで情報を整理
col1, col2 = st.columns(2)

with col1:
    st.header("🎬 動画関連")
    
    st.subheader("📥 入力対応形式")
    st.markdown("""
    **動画ファイル**:
    - MP4 (推奨)
    - AVI
    - MOV
    - MKV
    
    **音声ファイル (BGM)**:
    - MP3 (推奨)
    - WAV
    - AAC
    - M4A
    - OGG
    """)
    
    st.subheader("📤 出力形式")
    st.markdown("""
    **動画出力**:
    - MP4 (H.264コーデック)
    - AAC音声エンコード
    
    **解像度**:
    - ショート動画: 1080×1920 (9:16)
    - スライド動画: 1920×1080 (16:9)
    """)

with col2:
    st.header("📊 文書・音声関連")
    
    st.subheader("📥 PowerPoint形式")
    st.markdown("""
    **対応形式**:
    - PPTX (推奨)
    - PPT
    
    **処理内容**:
    - テキスト抽出
    - 9:16画像生成
    - スライド順序保持
    """)
    
    st.subheader("🎤 音声合成 (VOICEVOX)")
    st.markdown("""
    **機能**:
    - 日本語テキスト読み上げ
    - 複数の音声キャラクター
    - 感情・速度調整
    
    **出力**:
    - WAV形式
    - 高品質音声
    """)

st.markdown("---")

# 技術仕様セクション
st.header("⚙️ 技術仕様・制限事項")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🔧 処理能力")
    st.markdown("""
    **ファイルサイズ**:
    - 動画: 500MB以下推奨
    - PowerPoint: 100MB以下
    - BGM: 50MB以下
    
    **処理時間**:
    - ショート動画変換: 1-5分
    - 動画結合: 2-10分
    - スライド動画: 3-15分
    """)

with col2:
    st.subheader("🖥️ システム要件")
    st.markdown("""
    **動作環境**:
    - Docker対応システム
    - メモリ: 4GB以上推奨
    - ストレージ: 10GB以上推奨
    
    **ブラウザ**:
    - Chrome (推奨)
    - Firefox
    - Safari
    - Edge
    """)

with col3:
    st.subheader("⚠️ 注意事項")
    st.markdown("""
    **制限事項**:
    - 同時処理数: 1件
    - セッション時間: 60分
    - 一時ファイル自動削除
    
    **パフォーマンス**:
    - 大容量ファイルは処理時間増加
    - CPU使用率が高い場合あり
    - ネットワーク環境に依存
    """)

st.markdown("---")

# フォント情報
st.header("🔤 フォント・言語対応")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 日本語対応")
    st.markdown("""
    **使用フォント**:
    - Noto Sans CJK (メイン)
    - Noto Sans JP (サブ)
    
    **対応文字**:
    - ひらがな・カタカナ
    - 漢字 (JIS第一・第二水準)
    - 英数字・記号
    """)

with col2:
    st.subheader("🎨 テキスト表示")
    st.markdown("""
    **テロップ機能**:
    - 時間指定表示
    - フォントサイズ調整
    - 色・位置カスタマイズ
    
    **歌詞表示**:
    - 時間同期
    - カラオケ風エフェクト
    - 複数行対応
    """)

st.markdown("---")
st.info("💡 **詳細な使用方法**は「📖 使用方法」ページをご確認ください。")
st.warning("⚡ **大容量ファイル**の処理時は時間がかかる場合があります。処理中はブラウザを閉じないでください。")