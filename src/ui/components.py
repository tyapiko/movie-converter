"""UI components for the Streamlit application."""

import streamlit as st
from typing import List, Dict, Any, Optional
from src.audio import voicevox_client

class UIComponents:
    """Collection of reusable UI components."""
    
    @staticmethod
    def render_tool_selector() -> str:
        """Render the tool selection sidebar."""
        st.sidebar.title("🛠️ ツール選択")
        return st.sidebar.radio(
            "使用するツール",
            ["ショート動画変換", "動画結合", "スライド動画作成"]
        )
    
    @staticmethod
    def render_file_uploader(label: str, file_types: List[str], 
                           multiple: bool = False, key: str = None) -> Any:
        """Render a file uploader with specified types."""
        return st.file_uploader(
            label,
            type=file_types,
            accept_multiple_files=multiple,
            key=key
        )
    
    @staticmethod
    def render_telop_manager() -> List[Dict[str, Any]]:
        """Render telop (text overlay) management interface."""
        st.subheader("📝 テロップ設定")
        
        if 'telops' not in st.session_state:
            st.session_state.telops = []
        
        # Add new telop
        with st.expander("新しいテロップを追加"):
            col1, col2 = st.columns(2)
            with col1:
                start_time = st.number_input("開始時間 (秒)", min_value=0.0, step=0.1, key="telop_start")
                text = st.text_area("テキスト", key="telop_text")
            with col2:
                end_time = st.number_input("終了時間 (秒)", min_value=0.0, step=0.1, key="telop_end")
                position = st.selectbox("位置", ["bottom", "center", "top"], key="telop_position")
            
            if st.button("テロップを追加"):
                if text and end_time > start_time:
                    st.session_state.telops.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "text": text,
                        "position": position,
                        "font_size": 40
                    })
                    st.rerun()
        
        # Display existing telops
        if st.session_state.telops:
            st.subheader("追加済みテロップ")
            for i, telop in enumerate(st.session_state.telops):
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{telop['text']}** ({telop['start_time']}s - {telop['end_time']}s)")
                    with col2:
                        st.write(f"位置: {telop['position']}")
                    with col3:
                        if st.button("削除", key=f"delete_telop_{i}"):
                            st.session_state.telops.pop(i)
                            st.rerun()
        
        return st.session_state.telops
    
    @staticmethod
    def render_voice_settings() -> Dict[str, Any]:
        """Render voice synthesis settings."""
        st.subheader("🎤 音声合成設定")
        
        if not voicevox_client.is_connected():
            st.warning("⚠️ VOICEVOX サーバーに接続できません。音声合成機能は利用できません。")
            return None
        
        speakers = voicevox_client.get_speakers()
        if not speakers:
            st.error("話者情報を取得できませんでした。")
            return None
        
        # Create speaker options
        speaker_options = []
        speaker_map = {}
        
        for speaker in speakers:
            for style in speaker.get('styles', []):
                option_name = f"{speaker['name']} - {style['name']}"
                speaker_options.append(option_name)
                speaker_map[option_name] = style['id']
        
        col1, col2 = st.columns(2)
        with col1:
            selected_speaker = st.selectbox("話者", speaker_options)
            speed = st.slider("話速", 0.5, 2.0, 1.0, 0.1)
        with col2:
            pitch = st.slider("音高", -0.15, 0.15, 0.0, 0.01)
            intonation = st.slider("抑揚", 0.0, 2.0, 1.0, 0.1)
        
        return {
            "speaker_id": speaker_map[selected_speaker],
            "speed": speed,
            "pitch": pitch,
            "intonation": intonation
        }
    
    @staticmethod
    def render_video_settings() -> Dict[str, Any]:
        """Render video processing settings."""
        st.subheader("🎬 動画設定")
        
        col1, col2 = st.columns(2)
        with col1:
            scale_factor = st.slider("スケール", 0.5, 2.0, 1.0, 0.1, 
                                   help="動画のサイズ調整")
            start_time = st.number_input("開始時間 (秒)", min_value=0.0, 
                                       help="動画の開始位置")
        with col2:
            end_time = st.number_input("終了時間 (秒)", min_value=0.0, 
                                     help="動画の終了位置（0で全体）")
            quality = st.selectbox("品質", ["高品質", "標準", "高速"], 
                                 help="エンコード設定")
        
        return {
            "scale_factor": scale_factor,
            "start_time": start_time if start_time > 0 else None,
            "end_time": end_time if end_time > 0 else None,
            "quality": quality
        }
    
    @staticmethod
    def render_bgm_settings() -> Dict[str, Any]:
        """Render BGM settings."""
        st.subheader("🎵 BGM設定")
        
        bgm_file = st.file_uploader(
            "BGMファイルをアップロード",
            type=['mp3', 'wav', 'aac', 'm4a', 'ogg']
        )
        
        if bgm_file:
            volume = st.slider("BGM音量", 0.0, 1.0, 0.3, 0.1)
            return {"file": bgm_file, "volume": volume}
        
        return None
    
    @staticmethod
    def render_progress_indicator(message: str) -> None:
        """Render a progress indicator."""
        with st.spinner(message):
            st.empty()
    
    @staticmethod
    def render_slide_duration_settings(slide_count: int) -> List[float]:
        """Render slide duration settings."""
        st.subheader("⏱️ スライド表示時間設定")
        
        durations = []
        for i in range(slide_count):
            duration = st.number_input(
                f"スライド {i+1} の表示時間 (秒)",
                min_value=0.5,
                value=3.0,
                step=0.5,
                key=f"slide_duration_{i}"
            )
            durations.append(duration)
        
        return durations
    
    @staticmethod
    def render_lyrics_settings() -> List[Dict[str, Any]]:
        """Render lyrics settings interface."""
        st.subheader("🎤 歌詞設定")
        
        if 'lyrics' not in st.session_state:
            st.session_state.lyrics = []
        
        # Add new lyric
        with st.expander("新しい歌詞を追加"):
            col1, col2 = st.columns(2)
            with col1:
                lyric_start = st.number_input("開始時間 (秒)", min_value=0.0, step=0.1, key="lyric_start")
                lyric_text = st.text_input("歌詞", key="lyric_text")
            with col2:
                lyric_end = st.number_input("終了時間 (秒)", min_value=0.0, step=0.1, key="lyric_end")
            
            if st.button("歌詞を追加"):
                if lyric_text and lyric_end > lyric_start:
                    st.session_state.lyrics.append({
                        "start_time": lyric_start,
                        "end_time": lyric_end,
                        "text": lyric_text
                    })
                    st.rerun()
        
        # Display existing lyrics
        if st.session_state.lyrics:
            st.subheader("追加済み歌詞")
            for i, lyric in enumerate(st.session_state.lyrics):
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"**{lyric['text']}** ({lyric['start_time']}s - {lyric['end_time']}s)")
                    with col2:
                        if st.button("削除", key=f"delete_lyric_{i}"):
                            st.session_state.lyrics.pop(i)
                            st.rerun()
        
        return st.session_state.lyrics