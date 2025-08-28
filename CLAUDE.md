# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **YouTube Shorts Video Converter** - a comprehensive Streamlit web application that provides three main tools:

1. **Video Converter**: Converts videos to vertical format (9:16) with subtitle overlays, VOICEVOX voice synthesis, and BGM functionality
2. **Video Combiner**: Merges multiple video files into a single output
3. **Slide Video Creator**: Generates videos from PowerPoint presentations with background music and synchronized lyrics

The application runs in Docker containers for consistent deployment across different environments.

## Common Commands

### Development Commands
```bash
# Start development environment (with hot reload)
docker-compose -f docker-compose.dev.yml up -d

# Start production environment  
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f app
docker-compose logs -f voicevox
```

### Testing Commands
```bash
# Run basic automated tests
python3 test_basic.py

# Run test script (alternative)
bash run_tests.sh

# Manual health checks
curl -f http://localhost:8501/_stcore/health
curl -f http://localhost:50021/speakers  # VOICEVOX API
```

### Local Development (without Docker)
```bash
# Install dependencies
pip install -r requirements.txt

# Run application locally
streamlit run app.py

# Run on specific port
streamlit run app.py --server.port=8502
```

### Docker Management
```bash
# Rebuild containers
docker-compose build --no-cache

# Clean up resources
docker system prune -a

# View container stats
docker stats
```

## Architecture Overview

### Core Components
- **app.py**: Main Streamlit application with all video processing logic
- **Docker Services**: 
  - `app`: Main Streamlit application container
  - `voicevox`: VOICEVOX voice synthesis engine container
- **Processing Pipeline**: Upload → Resize → Add Text → Add Voice → Add BGM → Download

### Key Processing Functions

#### Video Conversion Functions
- `resize_video_to_shorts()`: Converts videos to 9:16 format using FFmpeg
- `add_text_to_video()`: Adds time-based text overlays using PIL/OpenCV
- `generate_voice_with_voicevox()`: Generates speech using VOICEVOX API
- `add_multiple_voices_to_video()`: Combines multiple audio tracks
- `add_bgm_to_video()`: Adds background music with looping

#### Video Processing Functions
- `combine_videos()`: Concatenates multiple video files

#### Slide Video Functions
- `extract_slides_from_pptx()`: Extracts text content from PowerPoint slides and generates 9:16 images
- `create_slide_video()`: Converts slide images to video with BGM and lyrics
- `add_lyrics_to_video()`: Overlays synchronized lyrics on video frames

### Dependencies
- **Video Processing**: MoviePy, OpenCV, FFmpeg
- **UI Framework**: Streamlit  
- **Voice Synthesis**: VOICEVOX (external container)
- **Image Processing**: PIL (Pillow)
- **PowerPoint Processing**: python-pptx
- **Japanese Font Support**: NotoSansCJK fonts
- **HTTP Requests**: requests

### File Structure
```
/app/
├── app.py                    # Main application
├── requirements.txt          # Python dependencies
├── fonts/                    # Japanese font files
│   └── NotoSansJP-Regular.ttf
├── tmp/                      # Temporary processing files
└── NotoSansCJK-Regular.ttc   # CJK font file
```

### Environment Configuration
- **VOICEVOX_URL**: Connection URL for VOICEVOX service (default: http://voicevox:50021)
- **Docker Networks**: Isolated networking between app and voicevox containers
- **Volume Mounts**: ./tmp:/app/tmp for temporary file sharing

## Development Patterns

### Error Handling
- Graceful degradation for VOICEVOX failures (continues without voice)
- Comprehensive cleanup of temporary files in try/finally blocks
- User-friendly error messages with specific guidance

### State Management  
- Streamlit session state for managing telops/voices lists
- Temporary file handling with proper cleanup
- Progress bars for long-running operations

### Processing Workflows

#### Video Conversion Workflow
1. **Input Validation**: File type and size checks
2. **Temporary Storage**: Secure temporary file creation
3. **Sequential Processing**: Resize → Text → Voice → BGM 
4. **Resource Cleanup**: Proper disposal of video clips and audio files
5. **Download Delivery**: Final file download with appropriate naming

#### Video Combination Workflow
1. **Multi-file Upload**: Accept multiple video files
2. **Validation**: Check file integrity and format compatibility
3. **Sequential Concatenation**: Merge videos in upload order
4. **Output Generation**: Single combined video file

#### Slide Video Creation Workflow
1. **PowerPoint Processing**: Extract slide content using python-pptx
2. **Image Generation**: Create 9:16 slide images with text rendering
3. **Duration Configuration**: Individual slide timing setup
4. **Lyrics Integration**: Time-synchronized text overlay
5. **BGM Synchronization**: Background music with looping
6. **Video Composition**: Combine slides, audio, and lyrics into final video

### Voice Synthesis Integration
- Multi-environment VOICEVOX URL detection (Docker/WSL/localhost)
- Async voice generation with proper error handling  
- Multiple voice track composition with timing controls
- Volume balancing between original audio and synthesized voice

## Important Considerations

### Performance
- Large video files (>500MB) may cause memory issues
- FFmpeg processing is CPU-intensive 
- VOICEVOX voice generation can be slow
- Temporary files require adequate disk space

### Compatibility
- WSL environments need special VOICEVOX configuration
- Font rendering requires proper Japanese font installation
- FFmpeg must be available in system PATH

### Security Notes
- All uploaded files are processed in temporary directories
- Files are automatically cleaned up after processing
- No persistent storage of user data
- Container runs as non-root user (appuser)

### Testing Strategy
- `test_basic.py`: Automated health checks for both services
- `run_tests.sh`: Bash script with fallback testing
- Manual testing via web interface for full functionality
- Docker health checks for service monitoring

## Troubleshooting

### Common Issues
- **VOICEVOX connection fails**: Check if voicevox container is running
- **Font rendering issues**: Verify NotoSansCJK font files are present  
- **Port conflicts**: Use different ports if 8501/50021 are occupied
- **Memory errors**: Reduce video file sizes or increase Docker memory limits

### Debug Commands
```bash
# Check container status
docker-compose ps

# Access container shell
docker-compose exec app bash
docker-compose exec voicevox bash

# Monitor resource usage
docker stats

# Check logs for specific errors
docker-compose logs app | grep ERROR
```