# OpenPlayt Software

This directory contains two implementations of the Playt Player:

## 📁 Directory Structure

### `python-player/`
The original Python-based player implementation using clean architecture principles.
- Full-featured CLI player
- FFmpeg-based audio playback
- Command pattern, Observer pattern, Strategy/Adapter pattern
- Comprehensive test suite
- See `python-player/README.md` for details

### `web-player/`
A fully client-side JavaScript web application.
- No server required - runs entirely in the browser
- Standard ES modules (no frameworks)
- Web Audio API for playback
- Modern, responsive UI
- See `web-player/README.md` for details

## Quick Start

### Python Player
```bash
cd python-player
poetry install  # or pip install -r requirements.txt
poetry run python -m playt_player.interface.cli.player_cli /path/to/album.playt
```

### Web Player
1. Open `web-player/index.html` in a web browser
2. Click "Load .playt File" and select a .playt file
3. Start playing!

## Features

Both implementations support:
- Loading .playt cartridge files (zip archives with audio files)
- Queue management with automatic track advancement
- Play/pause/stop/next/previous controls
- Volume control
- Track seeking

## Differences

| Feature | Python Player | Web Player |
|---------|--------------|------------|
| Audio Backend | FFmpeg (ffplay) | Web Audio API |
| Interface | CLI | Web Browser |
| File Access | File system | Browser file picker |
| Dependencies | Python + FFmpeg | Just a browser |
| Architecture | Clean Architecture | ES Modules |

## Requirements

### Python Player
- Python 3.11+
- FFmpeg (with ffplay)
- See `python-player/requirements.txt`

### Web Player
- Modern web browser (Chrome, Firefox, Safari, Edge)
- No installation required!

