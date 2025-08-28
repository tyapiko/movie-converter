"""Text overlay functionality for videos."""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip
from typing import List, Tuple, Dict, Any
from src.config import get_available_font
from src.utils import create_temp_file

class TextOverlay:
    """Handle text overlay operations on videos."""
    
    def __init__(self):
        self.font_path = get_available_font()
    
    def add_text_to_video(self, video_path: str, output_path: str, 
                         telops: List[Dict[str, Any]]) -> bool:
        """
        Add text overlays to video.
        
        Args:
            video_path: Input video path
            output_path: Output video path
            telops: List of telop dictionaries with keys:
                   - start_time: Start time in seconds
                   - end_time: End time in seconds
                   - text: Text content
                   - position: Text position (optional)
                   - font_size: Font size (optional)
                   
        Returns:
            bool: Success status
        """
        try:
            clip = VideoFileClip(video_path)
            
            def make_frame(get_frame, t):
                frame = get_frame(t)
                
                # Convert to PIL Image for text rendering
                pil_image = Image.fromarray(frame)
                draw = ImageDraw.Draw(pil_image)
                
                # Add telops that should be visible at time t
                for telop in telops:
                    if telop['start_time'] <= t <= telop['end_time']:
                        self._draw_text_on_image(
                            draw, pil_image, telop
                        )
                
                # Convert back to numpy array
                return np.array(pil_image)
            
            # Apply text overlay
            final_clip = clip.fl(lambda gf, t: make_frame(gf, t), apply_to=['mask'])
            
            # Write video
            final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            # Clean up
            clip.close()
            final_clip.close()
            
            return True
            
        except Exception as e:
            print(f"Text overlay error: {str(e)}")
            return False
    
    def _draw_text_on_image(self, draw: ImageDraw.Draw, image: Image.Image,
                           telop: Dict[str, Any]) -> None:
        """Draw text on PIL image."""
        text = telop['text']
        font_size = telop.get('font_size', 40)
        position = telop.get('position', 'bottom')
        
        try:
            font = ImageFont.truetype(self.font_path, font_size)
        except OSError:
            font = ImageFont.load_default()
        
        # Get text size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate position
        img_width, img_height = image.size
        
        if position == 'top':
            x = (img_width - text_width) // 2
            y = 50
        elif position == 'center':
            x = (img_width - text_width) // 2
            y = (img_height - text_height) // 2
        else:  # bottom
            x = (img_width - text_width) // 2
            y = img_height - text_height - 50
        
        # Draw text with outline
        outline_color = "black"
        text_color = "white"
        
        # Draw outline
        for adj in range(-2, 3):
            for adj2 in range(-2, 3):
                draw.text((x + adj, y + adj2), text, font=font, fill=outline_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)
    
    def create_slide_video(self, slides_data: List[Dict[str, Any]], 
                          bgm_path: str, output_path: str,
                          lyrics_data: List[Dict[str, Any]] = None) -> bool:
        """
        Create video from slide data.
        
        Args:
            slides_data: List of slide dictionaries
            bgm_path: Background music path
            output_path: Output video path
            lyrics_data: Optional lyrics data
            
        Returns:
            bool: Success status
        """
        try:
            from moviepy import ImageSequenceClip, AudioFileClip
            
            # Create slide images
            slide_paths = []
            total_duration = 0
            
            for i, slide in enumerate(slides_data):
                duration = slide.get('duration', 3.0)
                slide_image_path = create_temp_file(suffix=f"_slide_{i}.png")
                
                # Create slide image
                self._create_slide_image(slide, slide_image_path)
                slide_paths.append(slide_image_path)
                total_duration += duration
            
            # Create video from slides
            durations = [slide.get('duration', 3.0) for slide in slides_data]
            slide_clip = ImageSequenceClip(slide_paths, durations=durations)
            
            # Add BGM
            bgm_clip = AudioFileClip(bgm_path)
            if bgm_clip.duration < total_duration:
                loops_needed = int(total_duration / bgm_clip.duration) + 1
                bgm_clip = bgm_clip.loop(loops_needed).subclip(0, total_duration)
            else:
                bgm_clip = bgm_clip.subclip(0, total_duration)
            
            slide_clip = slide_clip.set_audio(bgm_clip)
            
            # Add lyrics if provided
            if lyrics_data:
                slide_clip = self._add_lyrics_to_video(slide_clip, lyrics_data)
            
            # Write video
            slide_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            # Clean up
            slide_clip.close()
            bgm_clip.close()
            
            return True
            
        except Exception as e:
            print(f"Slide video creation error: {str(e)}")
            return False
    
    def _create_slide_image(self, slide_data: Dict[str, Any], output_path: str) -> None:
        """Create an image from slide data."""
        from src.config import DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT
        
        # Create blank image
        img = Image.new('RGB', (DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT), 'white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype(self.font_path, 60)
            title_font = ImageFont.truetype(self.font_path, 80)
        except OSError:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
        
        # Draw title if present
        if 'title' in slide_data:
            title = slide_data['title']
            bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = bbox[2] - bbox[0]
            x = (DEFAULT_VIDEO_WIDTH - title_width) // 2
            draw.text((x, 100), title, font=title_font, fill='black')
        
        # Draw content
        if 'content' in slide_data:
            content = slide_data['content']
            lines = content.split('\n')
            y = 300
            
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                x = (DEFAULT_VIDEO_WIDTH - line_width) // 2
                draw.text((x, y), line, font=font, fill='black')
                y += 80
        
        # Save image
        img.save(output_path)
    
    def _add_lyrics_to_video(self, video_clip, lyrics_data: List[Dict[str, Any]]):
        """Add lyrics overlay to video."""
        def make_frame_with_lyrics(get_frame, t):
            frame = get_frame(t)
            pil_image = Image.fromarray(frame)
            draw = ImageDraw.Draw(pil_image)
            
            # Find current lyric
            for lyric in lyrics_data:
                if lyric['start_time'] <= t <= lyric['end_time']:
                    self._draw_text_on_image(draw, pil_image, {
                        'text': lyric['text'],
                        'font_size': 50,
                        'position': 'bottom'
                    })
                    break
            
            return np.array(pil_image)
        
        return video_clip.fl(lambda gf, t: make_frame_with_lyrics(gf, t), apply_to=['mask'])