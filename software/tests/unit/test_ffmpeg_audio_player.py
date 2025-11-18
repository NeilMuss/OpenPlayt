"""Unit tests for the FFmpeg audio player backend."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from playt_player.infrastructure.audio.ffmpeg_audio_player import FFmpegAudioPlayer


class DummyProcess:
    """Simple stand-in for subprocess.Popen in tests."""

    def __init__(self) -> None:
        self.pid = 1234
        self._terminated = False
        self._killed = False
        self._poll_value = None

    def poll(self) -> None:
        return self._poll_value

    def terminate(self) -> None:
        self._terminated = True

    def wait(self, timeout: float | None = None) -> None:
        return None

    def kill(self) -> None:
        self._killed = True


@patch("playt_player.infrastructure.audio.ffmpeg_audio_player.shutil.which", return_value=None)
def test_ffmpeg_audio_player_requires_ffplay(mock_which: MagicMock) -> None:
    """Ensure initialization fails if ffplay is unavailable."""
    with pytest.raises(RuntimeError):
        FFmpegAudioPlayer()


@patch("playt_player.infrastructure.audio.ffmpeg_audio_player.shutil.which", return_value="/usr/bin/ffplay")
def test_play_invokes_ffplay(mock_which: MagicMock) -> None:
    """Ensure play() shells out to ffplay."""
    dummy_process = DummyProcess()
    with patch(
        "playt_player.infrastructure.audio.ffmpeg_audio_player.subprocess.Popen",
        return_value=dummy_process,
    ) as mock_popen:
        player = FFmpegAudioPlayer()
        player.play("/tmp/song.mp3")

    mock_popen.assert_called_once_with(
        ["/usr/bin/ffplay", "-nodisp", "-autoexit", "-loglevel", "error", "/tmp/song.mp3"],
        stdin=subprocess.DEVNULL,  # type: ignore[arg-type]
    )
    assert player.is_playing()


@patch("playt_player.infrastructure.audio.ffmpeg_audio_player.shutil.which", return_value="/usr/bin/ffplay")
def test_pause_sends_sigstop_on_posix(mock_which: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure pause() sends SIGSTOP when supported."""
    player = FFmpegAudioPlayer()
    player._process = DummyProcess()  # type: ignore[attr-defined]
    player._state = "playing"  # type: ignore[attr-defined]
    player._current_file = "/tmp/song.mp3"  # type: ignore[attr-defined]
    monkeypatch.setattr(
        player, "_supports_posix_signals", lambda: True  # type: ignore[attr-defined]
    )

    with patch("playt_player.infrastructure.audio.ffmpeg_audio_player.os.kill") as mock_kill:
        player.pause()

    mock_kill.assert_called_once()
    assert player.get_state() in {"paused", "stopped", "idle"}

