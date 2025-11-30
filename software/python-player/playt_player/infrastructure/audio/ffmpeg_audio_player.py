"""FFmpeg-based audio player implementation using ffplay."""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import time
from typing import Optional

from ...domain.interfaces.audio_player import AudioPlayerInterface


class FFmpegAudioPlayer(AudioPlayerInterface):
    """
    Audio player implementation that shells out to ffplay.
    """

    def __init__(self, ffplay_path: Optional[str] = None) -> None:
        self._ffplay_path = ffplay_path or shutil.which("ffplay")
        if not self._ffplay_path:
            raise RuntimeError(
                "ffplay (part of ffmpeg) was not found on PATH. "
                "Install ffmpeg and ensure ffplay is available."
            )
        self._process: Optional[subprocess.Popen[bytes]] = None
        self._state: str = "idle"
        self._current_file: Optional[str] = None
        
        # Time tracking for position
        self._start_time: float = 0.0
        self._accumulated_time: float = 0.0
        
        # Volume (0.0 to 1.0), mapped to 0-100 for ffplay
        self._volume: float = 1.0

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #
    def _refresh_state(self) -> None:
        if self._process and self._process.poll() is not None:
            self._process = None
            self._state = "idle"
            self._current_file = None
            self._accumulated_time = 0.0
            self._start_time = 0.0

    def _terminate_process(self) -> None:
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()
        self._process = None
        # Don't clear _current_file here as we might be seeking/pausing

    def _supports_posix_signals(self) -> bool:
        return os.name == "posix"

    def _start_playback(self, file_path: str, start_pos: float = 0.0) -> None:
        """Start or restart playback from a specific position."""
        if not self._ffplay_path:
            raise RuntimeError("ffplay path not configured")

        if not file_path or not isinstance(file_path, (str, bytes, os.PathLike)):
             raise ValueError(f"Invalid file path: {file_path}")

        # Clamp volume between 0 and 100
        ff_volume = max(0, min(100, int(self._volume * 100)))

        cmd = [
            self._ffplay_path,
            "-nodisp",
            "-autoexit",
            "-loglevel",
            "error",
            "-volume",
            str(ff_volume),
            "-ss",
            str(start_pos),
            file_path,
        ]
        self._process = subprocess.Popen(cmd, stdin=subprocess.DEVNULL)
        self._current_file = file_path
        self._state = "playing"
        self._start_time = time.time()
        self._accumulated_time = start_pos

    # --------------------------------------------------------------------- #
    # AudioPlayerInterface implementation
    # --------------------------------------------------------------------- #
    def play(self, file_path: str) -> None:
        self._refresh_state()

        # Resume if paused and same file
        if (
            self._process
            and self._state == "paused"
            and self._current_file == file_path
            and self._supports_posix_signals()
        ):
            os.kill(self._process.pid, signal.SIGCONT)
            self._state = "playing"
            self._start_time = time.time()
            return

        # Stop existing if any
        self.stop()

        self._start_playback(file_path, 0.0)

    def pause(self) -> None:
        self._refresh_state()
        if not self._process or self._state != "playing":
            return

        if self._supports_posix_signals():
            os.kill(self._process.pid, signal.SIGSTOP)
            self._state = "paused"
            # Update accumulated time
            self._accumulated_time += time.time() - self._start_time
        else:
            # Best effort on non-POSIX: stop playback entirely.
            # We lose resume capability here unless we track it, 
            # but for now simple stop is safer.
            self.stop()

    def stop(self) -> None:
        if self._process:
            self._terminate_process()
        self._state = "stopped"
        self._current_file = None
        self._accumulated_time = 0.0
        self._start_time = 0.0

    def next(self) -> None:
        """Playlist management is handled by PlayerService."""
        pass

    def previous(self) -> None:
        """Playlist management is handled by PlayerService."""
        pass

    def seek(self, position_secs: float) -> None:
        if not self._current_file:
            return
            
        was_playing = (self._state == "playing" or self._state == "paused")
        if not was_playing:
            return
            
        # Stop current process
        if self._process:
            self._terminate_process()
            
        # Restart at new position
        self._start_playback(self._current_file, position_secs)

    def get_position(self) -> Optional[float]:
        self._refresh_state()
        if self._state == "playing":
            return self._accumulated_time + (time.time() - self._start_time)
        elif self._state == "paused":
            return self._accumulated_time
        return None

    def get_state(self) -> str:
        self._refresh_state()
        return self._state

    def is_playing(self) -> bool:
        self._refresh_state()
        return self._state == "playing"

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, volume))
        
        # If playing, we need to restart to apply volume change with ffplay
        # Capture current file and position before stopping
        current_file = self._current_file
        
        if self._state == "playing" and current_file:
            # Get current position to resume seamlessly
            pos = self.get_position() or 0.0
            
            self._terminate_process()
            self._start_playback(current_file, pos)

