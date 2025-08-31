# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **YouTube Shorts Video Converter** - a comprehensive Streamlit web application that provides three main tools:

1. **Video Converter**: Converts videos to vertical format (9:16) with subtitle overlays, VOICEVOX voice synthesis, and BGM functionality
2. **Video Combiner**: Merges multiple video files into a single output
3. **Slide Video Creator**: Generates videos from PowerPoint presentations with background music and synchronized lyrics

The application has been fully refactored (v2.0) from a monolithic structure to a modular architecture and includes GCP Cloud Run deployment capabilities.

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

### Code Quality
```bash
# Code formatting and linting (if tools are available)
ruff check src/
black src/
```

### GCP Deployment
```bash
# Deploy to Google Cloud Run (requires GCP project setup)
./deploy-gcp.sh YOUR_PROJECT_ID

# Build production Docker images
docker build -f Dockerfile.cloudrun -t movie-converter:cloudrun .
docker build -f Dockerfile.production -t movie-converter:production .
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

### Modular Architecture (v2.0)
The application has been refactored from a monolithic 2000+ line file into a clean modular structure:

```
src/
├── audio/              # VOICEVOX voice synthesis integration
│   └── voicevox.py     # VoiceVoxClient class with connection handling
├── config/             # Application configuration
│   └── settings.py     # Centralized settings, constants, and environment variables
├── ui/                 # Reusable UI components
│   └── components.py   # UIComponents class with Streamlit UI elements
├── utils/              # Utility functions
│   └── file_utils.py   # File handling, validation, and temporary file management
└── video/              # Video processing core
    ├── processor.py    # VideoProcessor class for resizing, BGM, combining
    └── text_overlay.py # TextOverlay class for telops and slide video creation
```

### Key Architecture Patterns

#### Modular Design
- **Single Responsibility**: Each module handles one specific domain
- **Dependency Injection**: Configuration and dependencies passed through constructors
- **Clean Interfaces**: Well-defined APIs between modules

#### Application Flow
1. **Main App** (`app.py`): Routes tool selection and coordinates UI components
2. **UI Components** (`src/ui/components.py`): Renders forms, file uploaders, settings panels
3. **Processing Classes**: Handle video manipulation, text overlay, and audio synthesis
4. **Configuration**: Centralized settings for paths, URLs, and application constants

#### Legacy Support
- **app_legacy.py**: Original monolithic version kept for compatibility
- **Gradual Migration**: New features use modular architecture, existing functions preserved

### Core Processing Pipeline
1. **File Upload & Validation**: File type checking and temporary storage
2. **Video Processing**: Resize/convert using VideoProcessor class
3. **Text & Audio Addition**: TextOverlay and VoiceVoxClient integration  
4. **Final Composition**: Combining all elements with proper resource cleanup
5. **Download Delivery**: Secure file delivery with automatic cleanup

### Deployment Architecture
- **Local Development**: Docker Compose with separate app/voicevox containers
- **Production (GCP)**: Cloud Run deployment with integrated or external VOICEVOX
- **Multi-Environment**: Different Dockerfiles for different deployment scenarios

### Environment Configuration
- **VOICEVOX_URL**: Connection URL for VOICEVOX service (default: http://voicevox:50021)
- **Docker Networks**: Isolated networking between app and voicevox containers
- **Volume Mounts**: ./tmp:/app/tmp for temporary file sharing
- **GCP Settings**: PROJECT_ID, CLOUD_STORAGE_BUCKET for production deployment

## Development Patterns

### Adding New Features
1. **Create Module**: Add new functionality in appropriate `src/` subdirectory
2. **UI Components**: Add reusable UI elements to `src/ui/components.py`
3. **Configuration**: Define new settings in `src/config/settings.py`  
4. **Integration**: Wire into main app through `app.py` tool routing
5. **Testing**: Add basic tests and manual validation

### Error Handling Philosophy
- **Graceful Degradation**: VOICEVOX failures don't break core functionality
- **Resource Cleanup**: Always use try/finally blocks for temporary files and video clips
- **User-Friendly Messages**: Clear error explanations with actionable guidance
- **Logging**: Important events and errors logged for debugging

### State Management Strategy
- **Session State**: Streamlit session_state for UI lists (telops, lyrics, voices)
- **Temporary Files**: Secure creation with automatic cleanup on completion/error
- **Progress Indicators**: Long operations show progress bars with status messages
- **Memory Management**: Explicit cleanup of MoviePy clips to prevent memory leaks

### VOICEVOX Integration Pattern
- **Multi-Environment Detection**: Tries multiple URLs (Docker/localhost/WSL)
- **Connection Resilience**: Falls back gracefully when VOICEVOX unavailable
- **API Abstraction**: VoiceVoxClient class encapsulates all VOICEVOX interactions
- **Error Recovery**: Continues processing even if voice synthesis fails

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