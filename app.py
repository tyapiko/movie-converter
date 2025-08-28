"""
動画編集ツール - リファクタリング版
YouTube Shorts Video Converter with modular architecture
"""

import streamlit as st
import tempfile
import os
from typing import Optional

# Local imports
from src.config import APP_TITLE, APP_ICON, APP_LAYOUT
from src.ui import UIComponents
from src.video import VideoProcessor, TextOverlay
from src.audio import voicevox_client
from src.utils import create_temp_file, cleanup_temp_files, is_supported_video, is_supported_presentation
from src.video.processor import VideoProcessor
from pptx import Presentation

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT
)

def main():
    """Main application entry point."""
    ui = UIComponents()
    
    # Tool selection
    selected_tool = ui.render_tool_selector()
    
    # Route to appropriate tool
    if selected_tool == "ショート動画変換":
        render_shorts_converter()
    elif selected_tool == "動画結合":
        render_video_combiner()
    else:  # スライド動画作成
        render_slide_video_creator()

def render_shorts_converter():
    """Render the YouTube Shorts converter interface."""
    st.title("🎬 ショート動画コンバーター")
    st.markdown("動画をアップロードして、YouTubeショート向けの縦型動画に変換しましょう！")
    
    ui = UIComponents()
    
    # File upload
    uploaded_video = ui.render_file_uploader(
        "動画ファイルをアップロード",
        ['mp4', 'avi', 'mov', 'mkv'],
        key="shorts_video"
    )
    
    if not uploaded_video:
        return
    
    # Video settings
    video_settings = ui.render_video_settings()
    
    # Text overlay option
    add_text = st.checkbox("テキストオーバーレイを追加")
    telops = []
    if add_text:
        telops = ui.render_telop_manager()
    
    # BGM settings
    bgm_settings = ui.render_bgm_settings()
    
    # Voice synthesis settings
    voice_settings = None
    if st.checkbox("音声合成を追加"):
        voice_settings = ui.render_voice_settings()
    
    # Process button
    if st.button("ショート動画に変換", type="primary"):
        process_shorts_conversion(
            uploaded_video, video_settings, telops, 
            bgm_settings, voice_settings
        )

def process_shorts_conversion(uploaded_video, video_settings, telops, bgm_settings, voice_settings):
    """Process the shorts conversion."""
    processor = VideoProcessor()
    text_overlay = TextOverlay()
    
    try:
        with st.spinner("動画を処理中..."):
            # Save uploaded video
            input_path = create_temp_file(suffix=".mp4")
            with open(input_path, "wb") as f:
                f.write(uploaded_video.read())
            
            # Step 1: Resize to shorts format
            resized_path = create_temp_file(suffix="_resized.mp4")
            success = processor.resize_to_shorts(
                input_path, resized_path,
                scale_factor=video_settings['scale_factor'],
                start_time=video_settings['start_time'],
                end_time=video_settings['end_time']
            )
            
            if not success:
                st.error("動画のリサイズに失敗しました")
                return
            
            current_video = resized_path
            
            # Step 2: Add text overlays
            if telops:
                with st.spinner("テキストオーバーレイを追加中..."):
                    text_video_path = create_temp_file(suffix="_with_text.mp4")
                    success = text_overlay.add_text_to_video(
                        current_video, text_video_path, telops
                    )
                    if success:
                        current_video = text_video_path
                    else:
                        st.warning("テキストオーバーレイの追加に失敗しました")
            
            # Step 3: Add voice synthesis
            if voice_settings and telops:
                with st.spinner("音声合成中..."):
                    # Generate voice for each telop
                    for telop in telops:
                        audio_data = voicevox_client.synthesize_speech(
                            telop['text'],
                            speaker=voice_settings['speaker_id'],
                            speed=voice_settings['speed'],
                            pitch=voice_settings['pitch'],
                            intonation=voice_settings['intonation']
                        )
                        if audio_data:
                            # Add audio to video (implementation needed)
                            pass
            
            # Step 4: Add BGM
            if bgm_settings:
                with st.spinner("BGMを追加中..."):
                    bgm_path = create_temp_file(suffix=".mp3")
                    with open(bgm_path, "wb") as f:
                        f.write(bgm_settings['file'].read())
                    
                    final_path = create_temp_file(suffix="_final.mp4")
                    success = processor.add_background_music(
                        current_video, bgm_path, final_path,
                        bgm_volume=bgm_settings['volume']
                    )
                    if success:
                        current_video = final_path
                    else:
                        st.warning("BGMの追加に失敗しました")
            
            # Provide download
            with open(current_video, "rb") as f:
                st.download_button(
                    label="変換済み動画をダウンロード",
                    data=f.read(),
                    file_name=f"shorts_{uploaded_video.name}",
                    mime="video/mp4"
                )
            
            st.success("✅ 動画変換が完了しました！")
    
    except Exception as e:
        st.error(f"❌ 処理中にエラーが発生しました: {str(e)}")
    
    finally:
        # Clean up temporary files
        cleanup_temp_files()

def render_video_combiner():
    """Render the video combiner interface."""
    st.title("🔗 動画結合ツール")
    st.markdown("複数のショート動画を選択して、長時間動画に結合しましょう！")
    
    ui = UIComponents()
    
    # Multiple file upload
    uploaded_videos = ui.render_file_uploader(
        "動画ファイルを複数選択",
        ['mp4', 'avi', 'mov', 'mkv'],
        multiple=True,
        key="combine_videos"
    )
    
    if not uploaded_videos or len(uploaded_videos) < 2:
        st.info("2つ以上の動画ファイルを選択してください")
        return
    
    # Display uploaded files
    st.subheader("アップロードされた動画")
    for i, video in enumerate(uploaded_videos):
        st.write(f"{i+1}. {video.name}")
    
    if st.button("動画を結合", type="primary"):
        process_video_combination(uploaded_videos)

def process_video_combination(uploaded_videos):
    """Process video combination."""
    processor = VideoProcessor()
    
    try:
        with st.spinner("動画を結合中..."):
            # Save uploaded videos
            video_paths = []
            for i, video in enumerate(uploaded_videos):
                temp_path = create_temp_file(suffix=f"_input_{i}.mp4")
                with open(temp_path, "wb") as f:
                    f.write(video.read())
                video_paths.append(temp_path)
            
            # Combine videos
            output_path = create_temp_file(suffix="_combined.mp4")
            success = processor.combine_videos(video_paths, output_path)
            
            if not success:
                st.error("動画結合に失敗しました")
                return
            
            # Provide download
            with open(output_path, "rb") as f:
                st.download_button(
                    label="結合済み動画をダウンロード",
                    data=f.read(),
                    file_name="combined_video.mp4",
                    mime="video/mp4"
                )
            
            st.success("✅ 動画結合が完了しました！")
    
    except Exception as e:
        st.error(f"❌ 処理中にエラーが発生しました: {str(e)}")
    
    finally:
        cleanup_temp_files()

def render_slide_video_creator():
    """Render the slide video creator interface."""
    st.title("📊 スライド動画作成ツール")
    st.markdown("PowerPointスライドと音楽から、歌詞付きの横型動画(16:9)を作成しましょう！")
    
    ui = UIComponents()
    
    # PowerPoint upload
    uploaded_ppt = ui.render_file_uploader(
        "PowerPointファイルをアップロード",
        ['pptx', 'ppt'],
        key="slide_ppt"
    )
    
    # BGM upload
    bgm_settings = ui.render_bgm_settings()
    
    if not uploaded_ppt or not bgm_settings:
        st.info("PowerPointファイルとBGMファイルの両方をアップロードしてください")
        return
    
    # Extract slides
    try:
        ppt_path = create_temp_file(suffix=".pptx")
        with open(ppt_path, "wb") as f:
            f.write(uploaded_ppt.read())
        
        slides_data = extract_slides_from_pptx(ppt_path)
        
        if not slides_data:
            st.error("スライドデータを抽出できませんでした")
            return
        
        st.success(f"✅ {len(slides_data)}枚のスライドを抽出しました")
        
        # Duration settings
        durations = ui.render_slide_duration_settings(len(slides_data))
        for i, duration in enumerate(durations):
            slides_data[i]['duration'] = duration
        
        # Lyrics settings
        lyrics_data = ui.render_lyrics_settings()
        
        if st.button("スライド動画を生成", type="primary"):
            process_slide_video_creation(slides_data, bgm_settings, lyrics_data)
    
    except Exception as e:
        st.error(f"❌ PowerPointファイルの処理に失敗しました: {str(e)}")

def extract_slides_from_pptx(ppt_path: str) -> list:
    """Extract slide data from PowerPoint file."""
    try:
        prs = Presentation(ppt_path)
        slides_data = []
        
        for i, slide in enumerate(prs.slides):
            slide_data = {"title": f"スライド {i+1}", "content": ""}
            
            # Extract text from shapes
            text_content = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    text_content.append(shape.text.strip())
            
            if text_content:
                slide_data["title"] = text_content[0] if text_content else f"スライド {i+1}"
                slide_data["content"] = "\n".join(text_content[1:]) if len(text_content) > 1 else ""
            
            slides_data.append(slide_data)
        
        return slides_data
    
    except Exception as e:
        st.error(f"スライド抽出エラー: {str(e)}")
        return []

def process_slide_video_creation(slides_data, bgm_settings, lyrics_data):
    """Process slide video creation."""
    text_overlay = TextOverlay()
    
    try:
        with st.spinner("スライド動画を生成中..."):
            # Save BGM
            bgm_path = create_temp_file(suffix=".mp3")
            with open(bgm_path, "wb") as f:
                f.write(bgm_settings['file'].read())
            
            # Create video
            output_path = create_temp_file(suffix="_slide_video.mp4")
            success = text_overlay.create_slide_video(
                slides_data, bgm_path, output_path, lyrics_data
            )
            
            if not success:
                st.error("スライド動画の生成に失敗しました")
                return
            
            # Provide download
            with open(output_path, "rb") as f:
                st.download_button(
                    label="スライド動画をダウンロード",
                    data=f.read(),
                    file_name="slide_video.mp4",
                    mime="video/mp4"
                )
            
            st.success("✅ スライド動画の生成が完了しました！")
    
    except Exception as e:
        st.error(f"❌ 処理中にエラーが発生しました: {str(e)}")
    
    finally:
        cleanup_temp_files()

if __name__ == "__main__":
    main()