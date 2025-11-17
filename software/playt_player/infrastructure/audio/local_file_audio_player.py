"""Local file audio player implementation using VLC as the backend."""

from typing import Optional

try:
    import vlc
except ImportError:
    vlc = None  # type: ignore

from ...domain.interfaces.audio_player import AudioPlayerInterface


class LocalFileAudioPlayer(AudioPlayerInterface):
    """
    Audio player implementation using VLC for local file playback.

    This is a concrete implementation of AudioPlayerInterface that uses
    the VLC library for actual audio playback.
    """

    def __init__(self) -> None:
        """Initialize the VLC player instance."""
        if vlc is None:
            raise ImportError(
                "python-vlc is not installed. Install it with: poetry add python-vlc"
            )
        self._instance = vlc.Instance()
        self._player: Optional[vlc.MediaPlayer] = None
        self._current_file: Optional[str] = None

    def play(self, file_path: str) -> None:
        """Start playing an audio file."""
        if self._player is not None:
            self.stop()

        media = self._instance.media_new(file_path)
        self._player = self._instance.media_player_new()
        self._player.set_media(media)
        self._player.play()
        self._current_file = file_path

    def pause(self) -> None:
        """Pause the currently playing audio."""
        if self._player is not None:
            self._player.pause()

    def stop(self) -> None:
        """Stop the currently playing audio."""
        if self._player is not None:
            self._player.stop()
            self._player = None
            self._current_file = None

    def next(self) -> None:
        """Skip to the next track (not implemented for single file playback)."""
        # For playlist support, this would need playlist management
        pass

    def previous(self) -> None:
        """Go to the previous track (not implemented for single file playback)."""
        # For playlist support, this would need playlist management
        pass

    def seek(self, position_secs: float) -> None:
        """Seek to a specific position in the current track."""
        if self._player is not None:
            # VLC uses milliseconds
            self._player.set_time(int(position_secs * 1000))

    def get_position(self) -> Optional[float]:
        """Get the current playback position in seconds."""
        if self._player is not None:
            # VLC returns milliseconds
            time_ms = self._player.get_time()
            if time_ms >= 0:
                return time_ms / 1000.0
        return None

    def get_state(self) -> str:
        """Get the current playback state."""
        if self._player is None:
            return "idle"

        state = self._player.get_state()
        if state == vlc.State.Playing:
            return "playing"
        elif state == vlc.State.Paused:
            return "paused"
        elif state == vlc.State.Stopped:
            return "stopped"
        else:
            return "idle"

    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        return self.get_state() == "playing"


