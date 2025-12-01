# Playt Player - Web Edition

A fully client-side JavaScript web application for playing .playt cartridge files. No server required - runs entirely in the browser using standard ES modules.

## Features

- Load and play .playt files (zip archives containing audio files)
- Queue management with automatic track advancement
- Play/pause/stop/next/previous controls
- Progress bar with seeking
- Volume control
- Queue display
- Modern, responsive UI with dark theme

## How to Use

1. Open `index.html` in a modern web browser (Chrome, Firefox, Safari, Edge)
   - **Note:** If you see old styling, do a hard refresh:
     - **Windows/Linux:** Press `Ctrl + Shift + R` or `Ctrl + F5`
     - **Mac:** Press `Cmd + Shift + R`
2. Click "Load Playt" and select a .playt file
3. The album will load and automatically start playing (if autoplay is allowed)

## File Structure

- `index.html` - Main HTML file with UI structure and styles
- `player.js` - Core player service with queue management and observer pattern
- `audio-loader.js` - Handles loading .playt zip files and extracting audio
- `ui.js` - UI controller that connects player service to the DOM

## Technical Details

- **No frameworks** - Pure vanilla JavaScript ES modules
- **Web Audio API** - Uses HTML5 Audio for playback
- **JSZip** - Loaded via CDN for extracting .playt archives
- **Observer Pattern** - For decoupled state management
- **Client-side only** - All processing happens in the browser

## Browser Support

Requires a modern browser with support for:
- ES6 modules
- HTML5 Audio API
- File API
- Blob URLs

**Note:** Audio format support varies by browser:
- MP3, WAV, OGG are widely supported
- FLAC support is limited (works in Chrome, Firefox; not in Safari/Edge)
- M4A/AAC support varies by browser

Tested in Chrome, Firefox, Safari, and Edge (latest versions).

### Troubleshooting

If songs load but don't play:
1. Check browser console for error messages (Press F12)
2. Verify audio format is supported by your browser
3. Try clicking the play button manually (autoplay may be blocked)
4. Ensure audio files aren't corrupted

If you see old styling (light theme instead of dark):
- Do a hard refresh: `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
- Or clear your browser cache

## Differences from Python Version

- Uses Web Audio API instead of FFmpeg
- Loads .playt files directly in browser (no file system access)
- UI is web-based instead of CLI
- No server required - fully client-side
- Dark theme UI matching the Python player's web interface
