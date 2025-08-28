"""Application configuration and constants."""

import os
from typing import List

# Application settings
APP_TITLE = "動画編集ツール"
APP_ICON = "🎬"
APP_LAYOUT = "wide"

# VOICEVOX settings
VOICEVOX_URLS = [
    "http://voicevox:50021",
    "http://localhost:50021", 
    "http://127.0.0.1:50021"
]

# Video settings
YOUTUBE_SHORTS_WIDTH = 1080
YOUTUBE_SHORTS_HEIGHT = 1920
DEFAULT_VIDEO_WIDTH = 1920
DEFAULT_VIDEO_HEIGHT = 1080

# Audio settings
DEFAULT_SAMPLE_RATE = 22050
DEFAULT_CHANNELS = 1

# File settings
SUPPORTED_VIDEO_FORMATS = [".mp4", ".avi", ".mov", ".mkv"]
SUPPORTED_AUDIO_FORMATS = [".mp3", ".wav", ".aac", ".m4a", ".ogg"]
SUPPORTED_PRESENTATION_FORMATS = [".pptx", ".ppt"]

MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

# Font settings
FONT_PATHS = [
    "/app/NotoSansCJK-Regular.ttc",
    "/app/fonts/NotoSansJP-Regular.ttf",
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
]

# Temporary directory
TEMP_DIR = "/app/tmp"

def get_available_font() -> str:
    """Find and return the first available font path."""
    for font_path in FONT_PATHS:
        if os.path.exists(font_path):
            return font_path
    return FONT_PATHS[0]  # Fallback to first option