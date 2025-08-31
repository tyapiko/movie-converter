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
    st.title("📊 スライド動画作成ツール12 - ハイブリッド版")
    st.markdown("PowerPointスライドまたはPNG画像と音楽から、歌詞付きの動画を作成しましょう！")
    
    ui = UIComponents()
    
    # Choose input method
    input_method = st.radio(
        "入力方法を選択してください:",
        ["🤖 PowerPointファイル（自動変換）", "📁 PNGファイル（手動変換済み）"],
        key="input_method"
    )
    
    if input_method == "🤖 PowerPointファイル（自動変換）":
        st.info("💡 システムが自動でPowerPointをスライド画像に変換します")
        
        # PowerPoint upload
        uploaded_ppt = ui.render_file_uploader(
            "PowerPointファイルをアップロード",
            ['pptx', 'ppt'],
            key="slide_ppt"
        )
        
        slides_data = None
        if uploaded_ppt:
            with st.spinner("PowerPointファイルを処理中..."):
                slides_data = process_powerpoint_file(uploaded_ppt)
                
                if not slides_data:
                    st.error("❌ 自動変換に失敗しました。下記の手動方式をお試しください。")
                    st.info("👇 「PNGファイル（手動変換済み）」を選択して、PowerPointからPNGを出力してアップロードしてください")
                else:
                    st.success(f"✅ {len(slides_data)}枚のスライドを自動変換しました！")
    
    else:  # PNG files method
        # Instructions for manual method
        with st.expander("📋 手動変換の手順", expanded=True):
            st.markdown("""
            ### 🎯 確実にスライドの見た目を保持する方法
            
            1. **PowerPointでPNG出力:**
               - PowerPointで「ファイル」→「エクスポート」→「ファイル形式の変更」
               - 「PNG ポータブル ネットワーク グラフィックス」を選択
               - 「名前を付けて保存」→「すべてのスライド」を選択
               
            2. **出力されたPNGファイルをアップロード:**
               - 複数のPNGファイルが作成されます（slide1.png, slide2.png...）
               - これらのファイルを下記でまとめてアップロードしてください
               
            3. **メリット:**
               - ✅ フォント・色・レイアウトが完全保持
               - ✅ 画像・図表・アニメーションも正確
               - ✅ 環境に依存しない確実な品質
            """)
        
        # PNG files upload
        uploaded_pngs = st.file_uploader(
            "スライドPNGファイルをアップロード（複数選択可能）",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key="slide_pngs",
            help="PowerPointから出力したPNGファイルを選択してください。複数選択可能です。"
        )
        
        slides_data = None
        if uploaded_pngs:
            slides_data = process_png_files(uploaded_pngs)
    
    # Only proceed if we have slides_data
    if not slides_data:
        if input_method == "🤖 PowerPointファイル（自動変換）":
            st.info("PowerPointファイルをアップロードしてください")
        else:
            st.info("PNGファイルをアップロードしてください")
        return
    
    # BGM upload
    bgm_settings = ui.render_bgm_settings()
    
    if not bgm_settings:
        st.info("BGMファイルもアップロードしてください")
        return
    
    # Show slide preview
    with st.expander("🔍 スライドプレビュー", expanded=False):
        cols = st.columns(min(len(slides_data), 4))
        for i, slide in enumerate(slides_data[:4]):  # Show first 4 slides
            with cols[i]:
                try:
                    st.image(slide['image_path'], caption=f"スライド {i+1}", width=150)
                except:
                    st.write(f"スライド {i+1}")
        
        if len(slides_data) > 4:
            st.info(f"...他 {len(slides_data)-4} 枚のスライド")
    
    # Duration settings
    durations = ui.render_slide_duration_settings(len(slides_data))
    for i, duration in enumerate(durations):
        if i < len(slides_data):
            slides_data[i]['duration'] = duration
    
    # Lyrics settings
    lyrics_data = ui.render_lyrics_settings()
    
    if st.button("🎬 スライド動画を生成", type="primary"):
        process_slide_video_creation(slides_data, bgm_settings, lyrics_data)

def process_powerpoint_file(uploaded_ppt):
    """Process PowerPoint file with multiple strategies."""
    try:
        # Simple file saving approach
        import tempfile
        import os
        
        # Use system temporary directory
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp_file:
            uploaded_ppt.seek(0)
            file_content = uploaded_ppt.read()
            tmp_file.write(file_content)
            ppt_path = tmp_file.name
        
        print(f"DEBUG: Saved PowerPoint to: {ppt_path}")
        print(f"DEBUG: File size: {len(file_content)} bytes")
        
        # Try to extract slides with our best method
        slides_data = extract_slides_minimal(ppt_path)
        
        # Clean up temp file
        try:
            os.unlink(ppt_path)
        except:
            pass
            
        return slides_data
        
    except Exception as e:
        print(f"DEBUG: PowerPoint processing error: {e}")
        return []

def process_png_files(uploaded_pngs):
    """Process uploaded PNG files."""
    try:
        slides_data = []
        
        # Sort PNG files by name to maintain order
        png_files = sorted(uploaded_pngs, key=lambda x: x.name.lower())
        
        st.info(f"📄 {len(png_files)}枚のスライド画像を処理中...")
        
        for i, png_file in enumerate(png_files):
            try:
                # Save PNG file to temporary location
                png_file.seek(0)  # Reset file pointer
                png_data = png_file.read()
                temp_png_path = create_temp_file(suffix=f"_slide_{i+1}.png")
                
                with open(temp_png_path, "wb") as f:
                    f.write(png_data)
                
                # Verify it's a valid image and resize if needed
                from PIL import Image
                from src.config import DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT
                
                with Image.open(temp_png_path) as img:
                    print(f"DEBUG: Slide {i+1} original size: {img.size}")
                    
                    # Convert to RGB if needed (for RGBA or other formats)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Resize to video dimensions while maintaining aspect ratio
                    img_resized = resize_image_for_video(img, DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT)
                    
                    # Save resized image
                    final_png_path = create_temp_file(suffix=f"_resized_slide_{i+1}.png")
                    img_resized.save(final_png_path, 'PNG', quality=95)
                
                slide_data = {
                    "title": f"スライド {i+1}",
                    "content": f"PowerPointスライド {i+1}",
                    "image_path": final_png_path,
                    "duration": 3.0
                }
                slides_data.append(slide_data)
                
                print(f"DEBUG: Successfully processed slide {i+1}: {png_file.name}")
                
            except Exception as e:
                st.warning(f"⚠️ スライド {i+1} ({png_file.name}) の処理でエラーが発生しました: {str(e)}")
                continue
        
        if not slides_data:
            st.error("処理可能なスライドがありませんでした。PNG形式の画像ファイルを確認してください。")
            return []
        
        st.success(f"✅ {len(slides_data)}枚のスライドを準備完了！")
        return slides_data
        
    except Exception as e:
        st.error(f"❌ スライド処理に失敗しました: {str(e)}")
        import traceback
        print(f"DEBUG: Full error: {traceback.format_exc()}")
        return []

def resize_image_for_video(img, target_width: int, target_height: int):
    """Resize image for video while maintaining aspect ratio with padding."""
    from PIL import Image
    
    # Calculate scaling to fit within target dimensions
    img_width, img_height = img.size
    target_ratio = target_width / target_height
    img_ratio = img_width / img_height
    
    if img_ratio > target_ratio:
        # Image is wider than target ratio
        new_width = target_width
        new_height = int(target_width / img_ratio)
    else:
        # Image is taller than target ratio
        new_height = target_height
        new_width = int(target_height * img_ratio)
    
    # Resize image
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create target size image with background
    final_img = Image.new('RGB', (target_width, target_height), 'white')
    
    # Center the resized image
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    
    final_img.paste(img_resized, (x_offset, y_offset))
    
    return final_img

def extract_slides_minimal(ppt_path: str) -> list:
    """PowerPoint to PNG export automation - mimics File→Export→PNG."""
    import os
    import tempfile
    import shutil
    
    print(f"DEBUG: Starting PowerPoint PNG export automation")
    print(f"DEBUG: Input file: {ppt_path}")
    print(f"DEBUG: File exists: {os.path.exists(ppt_path)}")
    
    if os.path.exists(ppt_path):
        file_size = os.path.getsize(ppt_path)
        print(f"DEBUG: File size: {file_size} bytes")
    
    # Create output directory for PNG files
    output_dir = tempfile.mkdtemp(prefix="ppt_png_")
    print(f"DEBUG: Created output directory: {output_dir}")
    
    try:
        # Strategy 1: Try LibreOffice command line export
        slides_data = export_with_libreoffice(ppt_path, output_dir)
        if slides_data:
            return slides_data
            
        # Strategy 2: Try python-pptx with PIL rendering
        slides_data = export_with_python_pptx(ppt_path, output_dir)
        if slides_data:
            return slides_data
            
        # Strategy 3: Try Windows COM automation (if available)
        slides_data = export_with_com_automation(ppt_path, output_dir)
        if slides_data:
            return slides_data
            
        print("DEBUG: All export methods failed")
        return []
        
    finally:
        # Clean up temporary directory
        try:
            shutil.rmtree(output_dir, ignore_errors=True)
        except:
            pass

def export_with_libreoffice(ppt_path: str, output_dir: str) -> list:
    """Export using LibreOffice command line - most reliable method."""
    import subprocess
    import os
    import glob
    
    try:
        print("DEBUG: Attempting LibreOffice PNG export...")
        
        # LibreOffice command to export all slides as PNG
        cmd = [
            'libreoffice',
            '--headless',
            '--convert-to', 'png',
            '--outdir', output_dir,
            ppt_path
        ]
        
        print(f"DEBUG: Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=60,
            cwd=output_dir
        )
        
        print(f"DEBUG: LibreOffice exit code: {result.returncode}")
        print(f"DEBUG: LibreOffice stdout: {result.stdout}")
        print(f"DEBUG: LibreOffice stderr: {result.stderr}")
        
        if result.returncode == 0:
            # Find generated PNG files
            png_files = glob.glob(os.path.join(output_dir, "*.png"))
            png_files.sort()
            
            print(f"DEBUG: Found {len(png_files)} PNG files: {[os.path.basename(f) for f in png_files]}")
            
            if png_files:
                return create_slides_from_png_files(png_files)
                
    except subprocess.TimeoutExpired:
        print("DEBUG: LibreOffice export timed out")
    except FileNotFoundError:
        print("DEBUG: LibreOffice not found")
    except Exception as e:
        print(f"DEBUG: LibreOffice export error: {e}")
    
    return []

def export_with_python_pptx(ppt_path: str, output_dir: str) -> list:
    """Export using python-pptx with slide rendering."""
    try:
        print("DEBUG: Attempting python-pptx export...")
        
        from pptx import Presentation
        prs = Presentation(ppt_path)
        
        print(f"DEBUG: Loaded presentation with {len(prs.slides)} slides")
        
        png_files = []
        for i, slide in enumerate(prs.slides):
            # For now, create enhanced slide image with extracted text
            # TODO: In future, could implement actual slide rendering
            all_text = []
            title_text = f"スライド {i+1}"
            
            try:
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        text = shape.text.strip()
                        if not title_text or title_text == f"スライド {i+1}":
                            title_text = text
                        else:
                            all_text.append(text)
            except:
                pass
            
            # Create PNG file path
            png_path = os.path.join(output_dir, f"slide_{i+1:03d}.png")
            
            # Create enhanced slide image
            from src.config import DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT
            create_enhanced_slide_image_to_file(
                title_text, all_text, i+1, 
                DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT,
                png_path
            )
            
            png_files.append(png_path)
        
        print(f"DEBUG: Created {len(png_files)} PNG files with python-pptx")
        return create_slides_from_png_files(png_files)
        
    except Exception as e:
        print(f"DEBUG: python-pptx export error: {e}")
        return []

def export_with_com_automation(ppt_path: str, output_dir: str) -> list:
    """Export using Windows COM automation (PowerPoint automation)."""
    try:
        print("DEBUG: Attempting COM automation export...")
        
        # This would work on Windows with PowerPoint installed
        import win32com.client
        
        app = win32com.client.Dispatch("PowerPoint.Application")
        app.Visible = False
        
        presentation = app.Presentations.Open(ppt_path)
        
        # Export all slides as PNG
        for i in range(1, presentation.Slides.Count + 1):
            slide = presentation.Slides(i)
            png_path = os.path.join(output_dir, f"slide_{i:03d}.png")
            slide.Export(png_path, "PNG")
        
        presentation.Close()
        app.Quit()
        
        # Find created PNG files
        import glob
        png_files = glob.glob(os.path.join(output_dir, "*.png"))
        png_files.sort()
        
        print(f"DEBUG: COM automation created {len(png_files)} PNG files")
        return create_slides_from_png_files(png_files)
        
    except ImportError:
        print("DEBUG: COM automation not available (not Windows or no pywin32)")
    except Exception as e:
        print(f"DEBUG: COM automation error: {e}")
    
    return []

def create_slides_from_png_files(png_files: list) -> list:
    """Create slide data from PNG files."""
    slides_data = []
    
    for i, png_file in enumerate(png_files):
        # Copy PNG to our temp system
        final_png_path = create_temp_file(suffix=f"_exported_slide_{i+1}.png")
        
        try:
            import shutil
            shutil.copy2(png_file, final_png_path)
            
            slide_data = {
                "title": f"スライド {i+1}",
                "content": "",
                "image_path": final_png_path,
                "duration": 3.0
            }
            slides_data.append(slide_data)
            
        except Exception as e:
            print(f"DEBUG: Error copying PNG file {png_file}: {e}")
            continue
    
    print(f"DEBUG: Successfully created {len(slides_data)} slide data entries")
    return slides_data

def create_enhanced_slide_image_to_file(title: str, content_lines: list, slide_num: int, width: int, height: int, output_path: str):
    """Create enhanced slide image and save to specific file path."""
    from PIL import Image, ImageDraw, ImageFont
    
    # Create the enhanced slide image (reusing existing logic)
    img = Image.new('RGB', (width, height), '#ffffff')
    draw = ImageDraw.Draw(img)
    
    # Add gradient background
    for y in range(height):
        color_value = int(248 + (y / height) * 7)
        color = f"#{color_value:02x}{color_value:02x}{color_value:02x}"
        draw.line([(0, y), (width, y)], fill=color)
    
    # Load fonts
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 50)
        font_content = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 32)
        font_small = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 24)
    except OSError:
        try:
            font_title = ImageFont.truetype("fonts/NotoSansJP-Regular.ttf", 50)
            font_content = ImageFont.truetype("fonts/NotoSansJP-Regular.ttf", 32)
            font_small = ImageFont.truetype("fonts/NotoSansJP-Regular.ttf", 24)
        except OSError:
            font_title = ImageFont.load_default()
            font_content = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # Draw slide number
    draw.text((30, 30), f"{slide_num}", font=font_small, fill='#999999')
    
    # Draw title
    title_lines = wrap_text(title, font_title, width - 120, draw)
    y_pos = 120
    
    for line in title_lines[:2]:
        bbox = draw.textbbox((0, 0), line, font=font_title)
        title_width = bbox[2] - bbox[0]
        x = (width - title_width) // 2
        
        padding = 20
        draw.rectangle([
            x - padding, y_pos - 10,
            x + title_width + padding, y_pos + bbox[3] + 10
        ], fill='#e3f2fd', outline='#1976d2', width=2)
        
        draw.text((x, y_pos), line, font=font_title, fill='#1565c0')
        y_pos += 70
    
    # Draw content
    y_pos += 40
    for line in content_lines[:8]:
        if y_pos > height - 100:
            break
        if isinstance(line, str) and line.strip():
            wrapped_lines = wrap_text(line, font_content, width - 160, draw)
            for wrapped_line in wrapped_lines[:3]:
                if y_pos > height - 100:
                    break
                draw.text((80, y_pos), "•", font=font_content, fill='#666666')
                draw.text((110, y_pos), wrapped_line, font=font_content, fill='#333333')
                y_pos += 45
            y_pos += 10
    
    # Save to specified path
    img.save(output_path, 'PNG', quality=95)

def extract_slides_from_pptx(ppt_path: str) -> list:
    """Extract slide data from PowerPoint file with multiple fallback strategies."""
    print(f"DEBUG: extract_slides_from_pptx called with path: {ppt_path}")
    
    # Strategy 1: Try robust python-pptx extraction
    try:
        print("DEBUG: Attempting robust python-pptx extraction")
        slides_data = extract_slides_robust(ppt_path)
        if slides_data:
            print(f"DEBUG: Successfully extracted {len(slides_data)} slides using robust method")
            return slides_data
    except Exception as e:
        print(f"DEBUG: Robust extraction failed: {e}")
    
    # Strategy 2: Try simple text extraction
    try:
        print("DEBUG: Attempting simple text extraction")
        slides_data = extract_slides_simple(ppt_path)
        if slides_data:
            print(f"DEBUG: Successfully extracted {len(slides_data)} slides using simple method")
            return slides_data
    except Exception as e:
        print(f"DEBUG: Simple extraction failed: {e}")
    
    # Strategy 3: Create generic slides based on slide count
    try:
        print("DEBUG: Attempting generic slide creation")
        slides_data = create_generic_slides(ppt_path)
        if slides_data:
            print(f"DEBUG: Successfully created {len(slides_data)} generic slides")
            return slides_data
    except Exception as e:
        print(f"DEBUG: Generic slide creation failed: {e}")
    
    st.error("PowerPointファイルの処理に失敗しました。ファイルが破損している可能性があります。")
    return []

def extract_slides_robust(ppt_path: str) -> list:
    """Robust PowerPoint extraction with error handling."""
    import tempfile
    import shutil
    
    try:
        # Copy file to ensure proper access
        temp_ppt_path = create_temp_file(suffix=".pptx")
        shutil.copy2(ppt_path, temp_ppt_path)
        
        prs = Presentation(temp_ppt_path)
        slides_data = []
        
        from PIL import Image, ImageDraw, ImageFont
        from src.config import DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT
        
        for i, slide in enumerate(prs.slides):
            try:
                # Extract text with multiple methods
                all_text = []
                title_text = None
                
                # Method 1: Direct shape text extraction
                for shape in slide.shapes:
                    try:
                        if hasattr(shape, "text") and shape.text.strip():
                            text = shape.text.strip()
                            if not title_text and len(text) < 200:
                                title_text = text
                            else:
                                all_text.append(text)
                    except:
                        continue
                
                # Method 2: Try slide.placeholders if shapes fail
                if not all_text and not title_text:
                    try:
                        for placeholder in slide.placeholders:
                            if hasattr(placeholder, "text") and placeholder.text.strip():
                                text = placeholder.text.strip()
                                if not title_text:
                                    title_text = text
                                else:
                                    all_text.append(text)
                    except:
                        pass
                
                # Ensure we have at least a title
                if not title_text:
                    title_text = f"スライド {i+1}"
                
                # Create slide image
                slide_image_path = create_enhanced_slide_image(
                    title_text, all_text, i+1, DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT
                )
                
                slide_data = {
                    "title": title_text,
                    "content": "\n".join(all_text) if all_text else "",
                    "image_path": slide_image_path,
                    "duration": 3.0
                }
                slides_data.append(slide_data)
                
            except Exception as slide_error:
                print(f"DEBUG: Error processing slide {i+1}: {slide_error}")
                # Create fallback slide
                slide_data = {
                    "title": f"スライド {i+1}",
                    "content": "スライドの内容を読み込めませんでした",
                    "image_path": create_enhanced_slide_image(
                        f"スライド {i+1}", ["内容を読み込めませんでした"], i+1, 
                        DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT
                    ),
                    "duration": 3.0
                }
                slides_data.append(slide_data)
        
        return slides_data
        
    except Exception as e:
        print(f"DEBUG: Robust extraction error: {e}")
        return []

def extract_slides_simple(ppt_path: str) -> list:
    """Simple PowerPoint extraction focusing on basic text."""
    try:
        prs = Presentation(ppt_path)
        slides_data = []
        
        from src.config import DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT
        
        for i, slide in enumerate(prs.slides):
            # Simple text extraction
            slide_text = f"スライド {i+1}"
            content_lines = []
            
            try:
                # Get any text we can find
                for shape in slide.shapes:
                    try:
                        if hasattr(shape, "text_frame"):
                            for paragraph in shape.text_frame.paragraphs:
                                if paragraph.text.strip():
                                    content_lines.append(paragraph.text.strip())
                        elif hasattr(shape, "text") and shape.text.strip():
                            content_lines.append(shape.text.strip())
                    except:
                        continue
                        
                if content_lines:
                    slide_text = content_lines[0] if content_lines else f"スライド {i+1}"
                    content_text = "\n".join(content_lines[1:]) if len(content_lines) > 1 else ""
                else:
                    content_text = ""
                    
            except:
                content_text = ""
            
            # Create slide image
            slide_image_path = create_enhanced_slide_image(
                slide_text, content_text.split('\n') if content_text else [], i+1,
                DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT
            )
            
            slide_data = {
                "title": slide_text,
                "content": content_text,
                "image_path": slide_image_path,
                "duration": 3.0
            }
            slides_data.append(slide_data)
        
        return slides_data
        
    except Exception as e:
        print(f"DEBUG: Simple extraction error: {e}")
        return []

def create_generic_slides(ppt_path: str) -> list:
    """Create generic slides when all else fails."""
    try:
        prs = Presentation(ppt_path)
        slide_count = len(prs.slides)
        slides_data = []
        
        from src.config import DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT
        
        for i in range(slide_count):
            slide_image_path = create_enhanced_slide_image(
                f"スライド {i+1}", 
                [f"PowerPointスライド {i+1} の内容", "詳細な内容は元のファイルをご確認ください"], 
                i+1, DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT
            )
            
            slide_data = {
                "title": f"スライド {i+1}",
                "content": f"PowerPointスライド {i+1} の内容",
                "image_path": slide_image_path,
                "duration": 3.0
            }
            slides_data.append(slide_data)
        
        return slides_data
        
    except Exception as e:
        print(f"DEBUG: Generic slide creation error: {e}")
        return []

def create_enhanced_slide_image(title: str, content_lines: list, slide_num: int, width: int, height: int) -> str:
    """Create a beautiful slide image."""
    from PIL import Image, ImageDraw, ImageFont
    
    # Create slide image with gradient background
    img = Image.new('RGB', (width, height), '#ffffff')
    draw = ImageDraw.Draw(img)
    
    # Add subtle gradient background
    for y in range(height):
        color_value = int(248 + (y / height) * 7)  # 248 to 255
        color = f"#{color_value:02x}{color_value:02x}{color_value:02x}"
        draw.line([(0, y), (width, y)], fill=color)
    
    # Load fonts
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 50)
        font_content = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 32)
        font_small = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 24)
    except OSError:
        try:
            font_title = ImageFont.truetype("fonts/NotoSansJP-Regular.ttf", 50)
            font_content = ImageFont.truetype("fonts/NotoSansJP-Regular.ttf", 32)
            font_small = ImageFont.truetype("fonts/NotoSansJP-Regular.ttf", 24)
        except OSError:
            font_title = ImageFont.load_default()
            font_content = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # Draw slide number
    draw.text((30, 30), f"{slide_num}", font=font_small, fill='#999999')
    
    # Draw title with background box
    title_lines = wrap_text(title, font_title, width - 120, draw)
    y_pos = 120
    
    for line in title_lines[:2]:  # Max 2 title lines
        bbox = draw.textbbox((0, 0), line, font=font_title)
        title_width = bbox[2] - bbox[0]
        x = (width - title_width) // 2
        
        # Title background box
        padding = 20
        draw.rectangle([
            x - padding, y_pos - 10, 
            x + title_width + padding, y_pos + bbox[3] + 10
        ], fill='#e3f2fd', outline='#1976d2', width=2)
        
        draw.text((x, y_pos), line, font=font_title, fill='#1565c0')
        y_pos += 70
    
    # Draw content
    y_pos += 40
    for line in content_lines[:8]:  # Max 8 content lines
        if y_pos > height - 100:
            break
            
        if isinstance(line, str) and line.strip():
            wrapped_lines = wrap_text(line, font_content, width - 160, draw)
            for wrapped_line in wrapped_lines[:3]:  # Max 3 wrapped lines per content line
                if y_pos > height - 100:
                    break
                # Add bullet point
                draw.text((80, y_pos), "•", font=font_content, fill='#666666')
                draw.text((110, y_pos), wrapped_line, font=font_content, fill='#333333')
                y_pos += 45
            y_pos += 10
    
    # Save image
    slide_image_path = create_temp_file(suffix=f"_enhanced_slide_{slide_num}.png")
    img.save(slide_image_path, 'PNG', quality=95)
    return slide_image_path

def wrap_text(text: str, font, max_width: int, draw) -> list:
    """Wrap text to fit within specified width."""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines

def create_robust_temp_file(file_data: bytes, suffix: str) -> str:
    """Create a temporary file with robust error handling."""
    import os
    import tempfile
    
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            # Create temp file with different methods
            if attempt == 0:
                # Method 1: Use our standard temp directory
                temp_path = create_temp_file(suffix=suffix)
            elif attempt == 1:
                # Method 2: Use system temp directory
                fd, temp_path = tempfile.mkstemp(suffix=suffix)
                os.close(fd)
            else:
                # Method 3: Use current directory as fallback
                import uuid
                temp_path = f"./temp_{uuid.uuid4().hex[:8]}{suffix}"
            
            print(f"DEBUG: Attempt {attempt+1}: Creating temp file at {temp_path}")
            
            # Write file with atomic operation
            temp_path_writing = temp_path + ".writing"
            with open(temp_path_writing, "wb") as f:
                f.write(file_data)
                f.flush()  # Ensure data is written
                os.fsync(f.fileno())  # Force write to disk
            
            # Atomic rename
            os.rename(temp_path_writing, temp_path)
            
            # Verify file was written correctly
            if os.path.exists(temp_path) and os.path.getsize(temp_path) == len(file_data):
                # Verify we can read it back
                with open(temp_path, "rb") as f:
                    test_data = f.read(100)  # Read first 100 bytes
                    if test_data == file_data[:100]:
                        print(f"DEBUG: Successfully created temp file: {temp_path}")
                        return temp_path
                    else:
                        print(f"DEBUG: File verification failed for {temp_path}")
                        try:
                            os.remove(temp_path)
                        except:
                            pass
            else:
                print(f"DEBUG: File size verification failed for {temp_path}")
                try:
                    os.remove(temp_path)
                except:
                    pass
                
        except Exception as e:
            print(f"DEBUG: Temp file creation attempt {attempt+1} failed: {e}")
            continue
    
    print("DEBUG: All temp file creation attempts failed")
    return None

def extract_slides_fallback(ppt_path: str) -> list:
    """Fallback method: Extract content from PowerPoint and create detailed slides."""
    print("DEBUG: Using fallback slide extraction method")
    import os
    import stat
    
    try:
        # Check file permissions and properties
        file_stat = os.stat(ppt_path)
        print(f"DEBUG: PowerPoint file path: {ppt_path}")
        print(f"DEBUG: File size: {file_stat.st_size} bytes")
        print(f"DEBUG: File permissions: {oct(file_stat.st_mode)}")
        print(f"DEBUG: File exists: {os.path.exists(ppt_path)}")
        print(f"DEBUG: File readable: {os.access(ppt_path, os.R_OK)}")
        
        # Try to read the PowerPoint file
        prs = Presentation(ppt_path)
        slides_data = []
        
        from PIL import Image, ImageDraw, ImageFont
        from src.config import DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT
        
        print(f"DEBUG: Successfully loaded PowerPoint with {len(prs.slides)} slides")
        
        for i, slide in enumerate(prs.slides):
            print(f"DEBUG: === Processing slide {i+1} ===")
            
            # Debug slide properties
            print(f"DEBUG: Slide {i+1} has {len(slide.shapes)} shapes")
            print(f"DEBUG: Slide {i+1} layout: {slide.slide_layout.name if hasattr(slide.slide_layout, 'name') else 'Unknown'}")
            
            # Create slide image with better background
            img = Image.new('RGB', (DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT), '#f8f9fa')
            draw = ImageDraw.Draw(img)
            
            # Load fonts
            try:
                font_title = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 60)
                font_content = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 36)
                font_small = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 28)
            except OSError:
                try:
                    font_title = ImageFont.truetype("fonts/NotoSansJP-Regular.ttf", 60)
                    font_content = ImageFont.truetype("fonts/NotoSansJP-Regular.ttf", 36)
                    font_small = ImageFont.truetype("fonts/NotoSansJP-Regular.ttf", 28)
                except OSError:
                    font_title = ImageFont.load_default()
                    font_content = ImageFont.load_default()
                    font_small = ImageFont.load_default()
            
            # Extract all text content with better organization
            text_blocks = []
            title_text = None
            
            for j, shape in enumerate(slide.shapes):
                print(f"DEBUG: Shape {j+1}: Type={shape.shape_type.name if hasattr(shape.shape_type, 'name') else shape.shape_type}")
                
                if hasattr(shape, "text"):
                    text = shape.text.strip()
                    if text:
                        print(f"DEBUG: Shape {j+1} text: '{text[:100]}{'...' if len(text) > 100 else ''}'")
                        print(f"DEBUG: Shape {j+1} position: left={getattr(shape, 'left', 'N/A')}, top={getattr(shape, 'top', 'N/A')}")
                        
                        # Try to determine if this is a title based on position and size
                        if not title_text and (len(text) < 100 or 
                                             (hasattr(shape, 'top') and len(slide.shapes) > 1 and shape.top < slide.shapes[0].top)):
                            title_text = text
                            print(f"DEBUG: Using as title: {text[:50]}...")
                        else:
                            text_blocks.append(text)
                            print(f"DEBUG: Added to content blocks: {text[:50]}...")
                    else:
                        print(f"DEBUG: Shape {j+1} has empty text")
                else:
                    print(f"DEBUG: Shape {j+1} has no text attribute")
            
            # If no title was found, use the first text block
            if not title_text and text_blocks:
                title_text = text_blocks.pop(0)
            
            if not title_text:
                title_text = f"スライド {i+1}"
            
            print(f"DEBUG: Slide {i+1} title: {title_text[:50]}...")
            
            # Draw slide number in corner
            draw.text((20, 20), f"{i+1}", font=font_small, fill='#666666')
            
            # Draw title with background
            title_lines = []
            if title_text:
                # Split long titles
                words = title_text.split()
                current_line = ""
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    bbox = draw.textbbox((0, 0), test_line, font=font_title)
                    if bbox[2] - bbox[0] < DEFAULT_VIDEO_WIDTH - 100:
                        current_line = test_line
                    else:
                        if current_line:
                            title_lines.append(current_line)
                        current_line = word
                if current_line:
                    title_lines.append(current_line)
            
            # Draw title
            y_pos = 100
            for line in title_lines[:2]:  # 最大2行のタイトル
                bbox = draw.textbbox((0, 0), line, font=font_title)
                title_width = bbox[2] - bbox[0]
                x = (DEFAULT_VIDEO_WIDTH - title_width) // 2
                
                # Title background
                draw.rectangle([x-10, y_pos-5, x+title_width+10, y_pos+bbox[3]+5], fill='#e3f2fd', outline='#2196f3')
                draw.text((x, y_pos), line, font=font_title, fill='#1976d2')
                y_pos += 80
            
            # Draw content blocks
            y_pos += 60
            for block in text_blocks[:6]:  # 最大6個のテキストブロック
                # Split content into lines
                content_lines = []
                for paragraph in block.split('\n'):
                    if not paragraph.strip():
                        content_lines.append("")
                        continue
                        
                    words = paragraph.split()
                    current_line = ""
                    for word in words:
                        test_line = current_line + " " + word if current_line else word
                        bbox = draw.textbbox((0, 0), test_line, font=font_content)
                        if bbox[2] - bbox[0] < DEFAULT_VIDEO_WIDTH - 120:
                            current_line = test_line
                        else:
                            if current_line:
                                content_lines.append(current_line)
                            current_line = word
                    if current_line:
                        content_lines.append(current_line)
                
                # Draw content lines
                for line in content_lines[:12]:  # 各ブロック最大12行
                    if y_pos > DEFAULT_VIDEO_HEIGHT - 100:
                        break
                    
                    if line.strip():
                        x = 60
                        # Add bullet point for non-empty lines
                        if line != content_lines[0] or len(text_blocks) > 1:
                            draw.text((40, y_pos), "•", font=font_content, fill='#666666')
                        draw.text((x, y_pos), line, font=font_content, fill='#333333')
                    y_pos += 45
                
                y_pos += 20  # Space between blocks
            
            # Save slide image
            slide_image_path = create_temp_file(suffix=f"_enhanced_slide_{i+1}.png")
            img.save(slide_image_path, 'PNG', quality=95)
            
            slide_data = {
                "title": title_text,
                "content": "\n".join(text_blocks) if text_blocks else "",
                "image_path": slide_image_path,
                "duration": 3.0
            }
            slides_data.append(slide_data)
            print(f"DEBUG: Created enhanced slide {i+1} with image: {slide_image_path}")
        
        print(f"DEBUG: Successfully created {len(slides_data)} enhanced slides")
        return slides_data
    
    except Exception as e:
        print(f"DEBUG: Enhanced fallback error: {str(e)}")
        st.error(f"スライド作成エラー: {str(e)}")
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