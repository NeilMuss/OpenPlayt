"""
WebView-based UI implementation using pywebview.
"""

import json
import os
import threading
from typing import Any, List, Optional, Dict

import webview  # type: ignore

from ...application.player_service import PlayerService
from ...domain.interfaces.observer import Observer
from ...infrastructure.audio.visualization_stub import VisualizationStub
from ...infrastructure.logging.cli_logger import get_cli_logger


class PlaytJSApi:
    """API exposed to JavaScript."""
    
    def __init__(self, player_service: PlayerService, logger: Any) -> None:
        self._player_service = player_service
        self._logger = logger

    def log(self, message: str) -> None:
        """Log message from JS."""
        self._logger.info(f"[UI] {message}")
        
    def play(self) -> None:
        """Start playback."""
        self._logger.info("[UI] Play command received")
        self._player_service.play()
        
    def pause(self) -> None:
        """Pause playback."""
        self._logger.info("[UI] Pause command received")
        self._player_service.pause()
        
    def togglePlay(self) -> None:
        """Toggle playback state."""
        self._logger.info("[UI] Toggle Play command received")
        state = self._player_service.get_state()
        if state == "playing":
            self._player_service.pause()
        else:
            self._player_service.play()
            
    def next(self) -> None:
        """Skip to next track."""
        self._logger.info("[UI] Next command received")
        self._player_service.next()
        
    def previous(self) -> None:
        """Skip to previous track."""
        self._logger.info("[UI] Previous command received")
        self._player_service.previous()
        
    def seek(self, seconds: float) -> None:
        """Seek to position."""
        self._logger.info(f"[UI] Seek to {seconds}s command received")
        try:
            self._player_service.seek(float(seconds))
        except NotImplementedError:
            self._logger.warning("[UI] Seek not implemented in current audio backend")
            
    def setVolume(self, value: float) -> None:
        """Set volume (0.0-1.0)."""
        self._logger.info(f"[UI] Set volume to {value}")
        self._player_service.set_volume(float(value))

    def pickFile(self) -> None:
        """Open file picker to load a cartridge."""
        if not self._player_service:
            return
            
        # This needs to be run on the main thread usually, or via window
        # We don't have easy access to window here, but we can use webview.windows[0]
        if len(webview.windows) > 0:
            window = webview.windows[0]
            result = window.create_file_dialog(
                webview.OPEN_DIALOG, 
                allow_multiple=False, 
                file_types=('Playt Files (*.playt)', 'All files (*.*)')
            )
            
            if result and len(result) > 0:
                file_path = result[0]
                self._load_file(file_path)

    def _load_file(self, file_path: str) -> None:
        """Internal method to load a file."""
        from pathlib import Path
        from ...infrastructure.cartridge.playt_file_cartridge_reader import PlaytFileCartridgeReader
        
        path = Path(file_path)
        if not path.exists() or path.suffix.lower() != ".playt":
            self._logger.error(f"Invalid file: {file_path}")
            return
            
        self._logger.info(f"Loading file: {file_path}")
        
        # Create new reader (this will be attached to the API instance to keep alive)
        # Note: we should probably clean up the old one if it exists
        if hasattr(self, '_current_reader') and self._current_reader:
            self._current_reader.cleanup()
            
        reader = PlaytFileCartridgeReader()
        self._current_reader = reader # Keep alive
        
        cartridge = reader.read_cartridge(str(path))
        if cartridge:
            album = reader.load_album_from_cartridge(cartridge)
            if album:
                self._player_service.stop()
                self._player_service.load_album(album)
                self._player_service.play()


class WebViewUI(Observer):
    """
    Manages the WebView window and communication between Python and JS.
    """

    def __init__(
        self, 
        player_service: PlayerService, 
        html_path: str,
        visualization_stub: Optional[VisualizationStub] = None
    ) -> None:
        self._player_service = player_service
        self._html_path = html_path
        self._visualization_stub = visualization_stub
        self._logger = get_cli_logger()
        self._window: Optional[webview.Window] = None
        self._js_api = PlaytJSApi(self._player_service, self._logger)
        self._progress_thread: Optional[threading.Thread] = None
        self._running = False

    def run(self) -> None:
        """Create and run the WebView window."""
        # Attach self as observer to player service
        self._player_service.attach(self)
        
        # Setup visualization callbacks if stub is present
        if self._visualization_stub:
            self._visualization_stub.set_callbacks(
                on_spectrum=self._on_spectrum,
                on_rms=self._on_rms,
                on_amplitude=self._on_amplitude
            )

        self._window = webview.create_window(
            "Playt Player",
            url=f"file://{self._html_path}",
            js_api=self._js_api,
            width=1024,
            height=768,
            min_size=(600, 400)
        )
        
        # Register start callback to inject the bridge
        webview.start(self._on_ready, debug=False)

    def update(self, event_type: str, data: Any) -> None:
        """Receive updates from PlayerService."""
        if not self._window:
            return
            
        try:
            if event_type == "track_started":
                # data is Song object
                song_data = {
                    "title": data.title,
                    "artist": data.artist,
                    "album": data.album,
                    "duration": data.duration_secs or 0,
                    "coverArt": data.cover_art_path,
                    "slideshowImages": data.slideshow_images
                }
                # Ensure unicode characters are preserved by disabling ascii escaping
                json_str = json.dumps(song_data, ensure_ascii=False)
                self._window.evaluate_js(f"window.playt._emitTrackChange({json_str})")
                self._window.evaluate_js("window.playt._emitPlaybackState('playing')")
                
            elif event_type == "track_paused":
                self._window.evaluate_js("window.playt._emitPlaybackState('paused')")
                
            elif event_type == "track_stopped":
                self._window.evaluate_js("window.playt._emitPlaybackState('stopped')")
                
            elif event_type == "album_loaded":
                # Album loaded but not necessarily playing
                # We might want to send the first track info if available
                queue = self._player_service.get_queue()
                if queue:
                    song = queue[0]
                    song_data = {
                        "title": song.title,
                        "artist": song.artist,
                        "album": song.album,
                        "duration": song.duration_secs or 0,
                        "coverArt": song.cover_art_path,
                        "slideshowImages": song.slideshow_images
                    }
                    # Ensure unicode characters are preserved by disabling ascii escaping
                    json_str = json.dumps(song_data, ensure_ascii=False)
                    self._window.evaluate_js(f"window.playt._emitTrackChange({json_str})")
                
        except Exception as e:
            self._logger.error(f"Error sending event to UI: {e}")

    def _on_ready(self) -> None:
        """Called when the window is loaded."""
        if not self._window:
            return

        self._logger.info("WebView UI started")
        self._running = True
        
        # Inject the JS bridge
        bridge_script = """
        window.playt = {
            _listeners: {
                ready: [],
                playbackState: [],
                trackChange: [],
                progress: [],
                spectrum: [],
                rms: [],
                amplitude: []
            },
            
            // Actions
            play: function() { pywebview.api.play(); },
            pause: function() { pywebview.api.pause(); },
            togglePlay: function() { pywebview.api.togglePlay(); },
            next: function() { pywebview.api.next(); },
            previous: function() { pywebview.api.previous(); },
            seek: function(seconds) { pywebview.api.seek(seconds); },
            setVolume: function(val) { pywebview.api.setVolume(val); },
            loadCartridge: function() { pywebview.api.pickFile(); },
            log: function(msg) { pywebview.api.log(msg); },

            // Event Subscriptions
            onReady: function(cb) { 
                this._listeners.ready.push(cb);
                setTimeout(() => cb(), 0);
            },
            onPlaybackState: function(cb) { this._listeners.playbackState.push(cb); },
            onTrackChange: function(cb) { this._listeners.trackChange.push(cb); },
            onProgress: function(cb) { this._listeners.progress.push(cb); },
            onSpectrum: function(cb) { this._listeners.spectrum.push(cb); },
            onRMS: function(cb) { this._listeners.rms.push(cb); },
            onAmplitude: function(cb) { this._listeners.amplitude.push(cb); },
            
            // Internal Emitters
            _emitPlaybackState: function(state) { 
                this._listeners.playbackState.forEach(cb => cb(state)); 
            },
            _emitTrackChange: function(track) { 
                this._listeners.trackChange.forEach(cb => cb(track)); 
            },
            _emitProgress: function(time) { 
                this._listeners.progress.forEach(cb => cb(time)); 
            },
            _emitSpectrum: function(data) { 
                this._listeners.spectrum.forEach(cb => cb(data)); 
            },
            _emitRMS: function(val) { 
                this._listeners.rms.forEach(cb => cb(val)); 
            },
            _emitAmplitude: function(val) { 
                this._listeners.amplitude.forEach(cb => cb(val)); 
            }
        };
        """
        self._window.evaluate_js(bridge_script)
        
        if self._visualization_stub:
            self._visualization_stub.start()
            
        # Start progress polling thread
        self._progress_thread = threading.Thread(target=self._poll_progress, daemon=True)
        self._progress_thread.start()
        
        # Initial state sync
        current_song = self._player_service.get_current_song()
        # If no current song but queue has items, show the first one
        if not current_song:
            queue = self._player_service.get_queue()
            if queue:
                current_song = queue[0]

        # Re-query because we might have just set it
        if current_song:
            song_data = {
                "title": current_song.title,
                "artist": current_song.artist,
                "album": current_song.album,
                "duration": current_song.duration_secs or 0,
                "coverArt": current_song.cover_art_path,
                "slideshowImages": current_song.slideshow_images
            }
            # Ensure unicode characters are preserved by disabling ascii escaping
            json_str = json.dumps(song_data, ensure_ascii=False)
            self._window.evaluate_js(f"window.playt._emitTrackChange({json_str})")
            
        state = self._player_service.get_state()
        self._window.evaluate_js(f"window.playt._emitPlaybackState('{state}')")

    def _poll_progress(self) -> None:
        """Poll for playback progress."""
        import time
        while self._running:
            # Check if track finished and auto-advance
            self._player_service.check_playback_status()
            
            if self._window and self._player_service.get_state() == "playing":
                pos = self._player_service.get_position()
                if pos is not None:
                    try:
                        self._window.evaluate_js(f"window.playt._emitProgress({pos})")
                    except Exception:
                        pass
            time.sleep(0.5)

    def _on_spectrum(self, data: List[float]) -> None:
        """Handle spectrum data from stub."""
        if self._window:
            try:
                self._window.evaluate_js(f"window.playt._emitSpectrum({json.dumps(data)})")
            except Exception:
                pass

    def _on_rms(self, val: float) -> None:
        """Handle RMS data from stub."""
        if self._window:
            try:
                self._window.evaluate_js(f"window.playt._emitRMS({val})")
            except Exception:
                pass
    
    def _on_amplitude(self, val: float) -> None:
        """Handle amplitude data from stub."""
        if self._window:
            try:
                self._window.evaluate_js(f"window.playt._emitAmplitude({val})")
            except Exception:
                pass

    def stop(self) -> None:
        """Stop the UI."""
        self._running = False
        if self._visualization_stub:
            self._visualization_stub.stop()
        if self._window:
            self._window.destroy()
