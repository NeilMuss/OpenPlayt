"""Player service coordinating audio playback and state management."""

from typing import Optional

from ..domain.entities.album import Album
from ..domain.entities.song import Song
from ..domain.interfaces.audio_player import AudioPlayerInterface
from ..domain.interfaces.observer import Subject


class PlayerService(Subject):
    """
    Service coordinating audio playback, queue management, and state notifications.

    This service acts as the application layer orchestrator, coordinating
    between the audio player, queue management, and observer notifications.
    """

    def __init__(self, audio_player: AudioPlayerInterface) -> None:
        """
        Initialize the player service.

        Args:
            audio_player: The audio player implementation to use
        """
        super().__init__()
        self._audio_player = audio_player
        self._current_song: Optional[Song] = None
        self._queue: list[Song] = []
        self._current_index: int = -1

    def load_album(self, album: Album) -> None:
        """
        Load an album into the playback queue.

        Args:
            album: The album to load
        """
        self._queue = album.ordered_songs()
        self._current_index = -1
        self._current_song = None
        self.notify("album_loaded", album)

    def load_queue(self, songs: list[Song]) -> None:
        """
        Load a custom queue of songs.

        Args:
            songs: List of songs to queue
        """
        self._queue = songs
        self._current_index = -1
        self._current_song = None
        self.notify("queue_loaded", songs)

    def play(self) -> None:
        """Start or resume playback."""
        if self._current_song is None and self._queue:
            self._current_index = 0
            self._current_song = self._queue[0]

        if self._current_song:
            self._audio_player.play(self._current_song.file_path)
            self.notify("track_started", self._current_song)

    def pause(self) -> None:
        """Pause playback."""
        if self._audio_player.is_playing():
            self._audio_player.pause()
            if self._current_song:
                self.notify("track_paused", self._current_song)

    def stop(self) -> None:
        """Stop playback."""
        self._audio_player.stop()
        if self._current_song:
            self.notify("track_stopped", self._current_song)
        self._current_song = None
        self._current_index = -1

    def next(self) -> None:
        """Skip to the next track in the queue."""
        if not self._queue:
            return

        if self._current_index < len(self._queue) - 1:
            self._current_index += 1
            self._current_song = self._queue[self._current_index]
            self._audio_player.play(self._current_song.file_path)
            self.notify("track_started", self._current_song)
        else:
            self.stop()
            self.notify("queue_ended", None)

    def previous(self) -> None:
        """Go to the previous track in the queue."""
        if not self._queue:
            return

        if self._current_index > 0:
            self._current_index -= 1
            self._current_song = self._queue[self._current_index]
            self._audio_player.play(self._current_song.file_path)
            self.notify("track_started", self._current_song)
        else:
            # Restart current track
            if self._current_song:
                self._audio_player.play(self._current_song.file_path)
                self.notify("track_started", self._current_song)

    def seek(self, position_secs: float) -> None:
        """
        Seek to a specific position in the current track.

        Args:
            position_secs: Position in seconds
        """
        self._audio_player.seek(position_secs)
        self.notify("seeked", {"position": position_secs, "song": self._current_song})

    def get_current_song(self) -> Optional[Song]:
        """
        Get the currently playing song.

        Returns:
            Current song or None if nothing is playing
        """
        return self._current_song

    def get_queue(self) -> list[Song]:
        """
        Get the current playback queue.

        Returns:
            List of songs in the queue
        """
        return self._queue.copy()

    def get_state(self) -> str:
        """
        Get the current playback state.

        Returns:
            State string from the audio player
        """
        return self._audio_player.get_state()

    def get_position(self) -> Optional[float]:
        """
        Get the current playback position.

        Returns:
            Position in seconds or None
        """
        return self._audio_player.get_position()

    def set_volume(self, volume: float) -> None:
        """
        Set the playback volume.

        Args:
            volume: Volume level from 0.0 to 1.0
        """
        self._audio_player.set_volume(volume)
        self.notify("volume_changed", volume)

    def check_playback_status(self) -> None:
        """
        Check the status of playback and advance if necessary.
        
        This method should be called periodically by the main loop.
        If the audio player reports 'idle' but we have a current song,
        it means the track finished naturally.
        """
        state = self._audio_player.get_state()
        
        # If we think we are playing (current_song is set) but player is idle,
        # then the track finished.
        if self._current_song is not None and state == "idle":
            # Advance to next track
            self.next()
