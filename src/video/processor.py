"""Video processing functions."""

import subprocess
import os
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
from typing import Optional, Tuple
from src.config import YOUTUBE_SHORTS_WIDTH, YOUTUBE_SHORTS_HEIGHT
from src.utils import create_temp_file

class VideoProcessor:
    """Handle video processing operations."""
    
    @staticmethod
    def resize_to_shorts(video_path: str, output_path: str, scale_factor: float = 1.0,
                        start_time: Optional[float] = None, 
                        end_time: Optional[float] = None) -> bool:
        """
        Resize video to YouTube Shorts format (9:16).
        
        Args:
            video_path: Input video path
            output_path: Output video path
            scale_factor: Scale factor for resizing
            start_time: Start time for clipping
            end_time: End time for clipping
            
        Returns:
            bool: Success status
        """
        try:
            # Get original video info
            clip = VideoFileClip(video_path)
            original_width, original_height = clip.size
            original_ratio = original_width / original_height
            clip.close()
            
            target_width = YOUTUBE_SHORTS_WIDTH
            target_height = YOUTUBE_SHORTS_HEIGHT
            target_ratio = target_width / target_height
            
            # Build FFmpeg command
            cmd = [
                "ffmpeg", "-i", video_path, "-y",
                "-vf"
            ]
            
            # Apply time range if specified
            time_filter = ""
            if start_time is not None and end_time is not None:
                cmd.extend(["-ss", str(start_time), "-t", str(end_time - start_time)])
            
            # Calculate scaling and padding
            if original_ratio > target_ratio:
                # Original is wider, scale by height and add horizontal padding
                new_height = int(target_height * scale_factor)
                new_width = int(new_height * original_ratio)
                pad_x = (target_width - new_width) // 2
                vf = f"scale={new_width}:{new_height},pad={target_width}:{target_height}:{pad_x}:0:black"
            else:
                # Original is taller, scale by width and add vertical padding
                new_width = int(target_width * scale_factor)
                new_height = int(new_width / original_ratio)
                pad_y = (target_height - new_height) // 2
                vf = f"scale={new_width}:{new_height},pad={target_width}:{target_height}:0:{pad_y}:black"
            
            cmd.extend([vf, "-c:a", "copy", output_path])
            
            # Execute FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Video resize error: {str(e)}")
            return False
    
    @staticmethod
    def add_background_music(video_path: str, bgm_path: str, output_path: str,
                           bgm_volume: float = 0.3) -> bool:
        """
        Add background music to video.
        
        Args:
            video_path: Input video path
            bgm_path: Background music path
            output_path: Output video path
            bgm_volume: BGM volume (0.0-1.0)
            
        Returns:
            bool: Success status
        """
        try:
            video_clip = VideoFileClip(video_path)
            bgm_clip = AudioFileClip(bgm_path)
            
            # Loop BGM to match video duration
            if bgm_clip.duration < video_clip.duration:
                loops_needed = int(video_clip.duration / bgm_clip.duration) + 1
                bgm_clip = bgm_clip.loop(loops_needed).subclip(0, video_clip.duration)
            else:
                bgm_clip = bgm_clip.subclip(0, video_clip.duration)
            
            # Adjust volume
            bgm_clip = bgm_clip.volumex(bgm_volume)
            
            # Combine audio
            if video_clip.audio:
                final_audio = CompositeAudioClip([video_clip.audio, bgm_clip])
            else:
                final_audio = bgm_clip
            
            # Set combined audio to video
            final_video = video_clip.set_audio(final_audio)
            
            # Write final video
            final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            # Clean up
            video_clip.close()
            bgm_clip.close()
            final_video.close()
            
            return True
            
        except Exception as e:
            print(f"BGM addition error: {str(e)}")
            return False
    
    @staticmethod
    def combine_videos(video_paths: list, output_path: str) -> bool:
        """
        Combine multiple videos into one.
        
        Args:
            video_paths: List of video file paths
            output_path: Output video path
            
        Returns:
            bool: Success status
        """
        try:
            from moviepy import concatenate_videoclips
            
            clips = []
            for path in video_paths:
                clip = VideoFileClip(path)
                clips.append(clip)
            
            final_clip = concatenate_videoclips(clips, method="compose")
            final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            # Clean up
            for clip in clips:
                clip.close()
            final_clip.close()
            
            return True
            
        except Exception as e:
            print(f"Video combination error: {str(e)}")
            return False