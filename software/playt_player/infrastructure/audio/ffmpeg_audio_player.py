"""FFmpeg-based audio player implementation using ffplay."""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
from typing import Optional

from ...domain.interfaces.audio_player import AudioPlayerInterface


class FFmpegAudioPlayer(AudioPlayerInterface):
    """
    Audio player implementation that shells out to ffplay.

    This implementation keeps the surface area intentionally small so it can run
    anywhere ffmpeg is available.  Pause/resume support relies on POSIX signals.
    On non-POSIX platforms pause simply stops playback.
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

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #
    def _refresh_state(self) -> None:
        if self._process and self._process.poll() is not None:
            self._process = None
            self._state = "idle"
            self._current_file = None

    def _terminate_process(self) -> None:
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()
        self._process = None
        self._current_file = None

    def _supports_posix_signals(self) -> bool:
        return os.name == "posix"

    # --------------------------------------------------------------------- #
    # AudioPlayerInterface implementation
    # --------------------------------------------------------------------- #
    def play(self, file_path: str) -> None:
        self._refresh_state()

        if (
            self._process
            and self._state == "paused"
            and self._current_file == file_path
            and self._supports_posix_signals()
        ):
            os.kill(self._process.pid, signal.SIGCONT)
            self._state = "playing"
            return

        self.stop()

        if not self._ffplay_path:
            raise RuntimeError("ffplay path not configured")

        cmd = [
            self._ffplay_path,
            "-nodisp",
            "-autoexit",
            "-loglevel",
            "error",
            file_path,
        ]
        self._process = subprocess.Popen(cmd, stdin=subprocess.DEVNULL)  # noqa: S603
        self._current_file = file_path
        self._state = "playing"

    def pause(self) -> None:
        self._refresh_state()
        if not self._process or self._state != "playing":
            return

        if self._supports_posix_signals():
            os.kill(self._process.pid, signal.SIGSTOP)
            self._state = "paused"
        else:
            # Best effort on non-POSIX: stop playback entirely.
            self.stop()

    def stop(self) -> None:
        if self._process:
            self._terminate_process()
        self._state = "stopped"

    def next(self) -> None:
        """Playlist management is handled by PlayerService."""
        # Not implemented at the audio backend level.
        pass

    def previous(self) -> None:
        """Playlist management is handled by PlayerService."""
        # Not implemented at the audio backend level.
        pass

    def seek(self, position_secs: float) -> None:
        raise NotImplementedError("FFmpegAudioPlayer does not support seeking yet.")

    def get_position(self) -> Optional[float]:
        self._refresh_state()
        return None

    def get_state(self) -> str:
        self._refresh_state()
        return self._state

    def is_playing(self) -> bool:
        self._refresh_state()
        return self._state == "playing"

