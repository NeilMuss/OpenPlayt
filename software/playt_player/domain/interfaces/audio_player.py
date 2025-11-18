"""Audio player interface following the Strategy/Adapter pattern."""

from abc import ABC, abstractmethod
from typing import Optional


class AudioPlayerInterface(ABC):
    """
    Abstract interface for audio playback.

    This interface allows different audio backends (ffmpeg, pydub, etc.)
    to be swapped without changing the application layer.
    """

    @abstractmethod
    def play(self, file_path: str) -> None:
        """
        Start playing an audio file.

        Args:
            file_path: Path to the audio file to play
        """
        pass

    @abstractmethod
    def pause(self) -> None:
        """Pause the currently playing audio."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the currently playing audio."""
        pass

    @abstractmethod
    def next(self) -> None:
        """Skip to the next track (if applicable)."""
        pass

    @abstractmethod
    def previous(self) -> None:
        """Go to the previous track (if applicable)."""
        pass

    @abstractmethod
    def seek(self, position_secs: float) -> None:
        """
        Seek to a specific position in the current track.

        Args:
            position_secs: Position in seconds
        """
        pass

    @abstractmethod
    def get_position(self) -> Optional[float]:
        """
        Get the current playback position.

        Returns:
            Current position in seconds, or None if not playing
        """
        pass

    @abstractmethod
    def get_state(self) -> str:
        """
        Get the current playback state.

        Returns:
            State string: 'playing', 'paused', 'stopped', or 'idle'
        """
        pass

    @abstractmethod
    def is_playing(self) -> bool:
        """
        Check if audio is currently playing.

        Returns:
            True if playing, False otherwise
        """
        pass


