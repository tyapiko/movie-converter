"""File handling utilities."""

import os
import tempfile
import glob
from typing import Optional
from src.config import TEMP_DIR

def ensure_temp_dir() -> None:
    """Ensure temporary directory exists."""
    os.makedirs(TEMP_DIR, exist_ok=True)

def create_temp_file(suffix: str = "") -> str:
    """Create a temporary file and return its path."""
    ensure_temp_dir()
    fd, path = tempfile.mkstemp(suffix=suffix, dir=TEMP_DIR)
    os.close(fd)
    return path

def cleanup_temp_files(pattern: str = "*") -> None:
    """Clean up temporary files matching pattern."""
    if os.path.exists(TEMP_DIR):
        files = glob.glob(os.path.join(TEMP_DIR, pattern))
        for file in files:
            try:
                os.remove(file)
            except OSError:
                pass

def get_file_extension(filename: str) -> str:
    """Get file extension in lowercase."""
    return os.path.splitext(filename)[1].lower()

def is_supported_video(filename: str) -> bool:
    """Check if file is a supported video format."""
    from src.config import SUPPORTED_VIDEO_FORMATS
    return get_file_extension(filename) in SUPPORTED_VIDEO_FORMATS

def is_supported_audio(filename: str) -> bool:
    """Check if file is a supported audio format."""
    from src.config import SUPPORTED_AUDIO_FORMATS
    return get_file_extension(filename) in SUPPORTED_AUDIO_FORMATS

def is_supported_presentation(filename: str) -> bool:
    """Check if file is a supported presentation format."""
    from src.config import SUPPORTED_PRESENTATION_FORMATS
    return get_file_extension(filename) in SUPPORTED_PRESENTATION_FORMATS