"""Integration tests for the complete player workflow."""

import tempfile
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock

import pytest

from playt_player.application.player_service import PlayerService
from playt_player.domain.entities.album import Album
from playt_player.domain.entities.song import Song
from playt_player.domain.interfaces.audio_player import AudioPlayerInterface
from playt_player.infrastructure.cartridge.local_file_cartridge_reader import (
    LocalFileCartridgeReader,
)


class MockAudioPlayer(AudioPlayerInterface):
    """Mock audio player for testing without actual audio playback."""

    def __init__(self) -> None:
        """Initialize the mock player."""
        self._state = "idle"
        self._position = 0.0
        self._current_file: Optional[str] = None
        self._play_calls: list[str] = []

    def play(self, file_path: str) -> None:
        """Start playing an audio file."""
        self._current_file = file_path
        self._state = "playing"
        self._play_calls.append(file_path)

    def pause(self) -> None:
        """Pause playback."""
        if self._state == "playing":
            self._state = "paused"

    def stop(self) -> None:
        """Stop playback."""
        self._state = "stopped"
        self._current_file = None
        self._position = 0.0

    def next(self) -> None:
        """Not implemented for mock."""
        pass

    def previous(self) -> None:
        """Not implemented for mock."""
        pass

    def seek(self, position_secs: float) -> None:
        """Seek to position."""
        self._position = position_secs

    def get_position(self) -> Optional[float]:
        """Get current position."""
        return self._position if self._state != "idle" else None

    def get_state(self) -> str:
        """Get current state."""
        return self._state

    def is_playing(self) -> bool:
        """Check if playing."""
        return self._state == "playing"


class TestPlayerIntegration:
    """Integration tests for complete player workflows."""

    def test_load_and_play_album(self) -> None:
        """Test loading an album and playing it."""
        audio_player = MockAudioPlayer()
        player_service = PlayerService(audio_player)

        song1 = Song(
            title="Song 1",
            artist="Test Artist",
            album="Test Album",
            duration_secs=100.0,
            file_path="/path/to/1.mp3",
            track_number=1,
        )
        song2 = Song(
            title="Song 2",
            artist="Test Artist",
            album="Test Album",
            duration_secs=200.0,
            file_path="/path/to/2.mp3",
            track_number=2,
        )
        album = Album(title="Test Album", artist="Test Artist", songs=[song1, song2])

        # Load album
        player_service.load_album(album)
        assert len(player_service.get_queue()) == 2

        # Play first song
        player_service.play()
        assert player_service.get_current_song() == song1
        assert audio_player.get_state() == "playing"
        assert "/path/to/1.mp3" in audio_player._play_calls

        # Skip to next song
        player_service.next()
        assert player_service.get_current_song() == song2
        assert "/path/to/2.mp3" in audio_player._play_calls

    def test_observer_notifications(self) -> None:
        """Test that observers receive notifications during playback."""
        audio_player = MockAudioPlayer()
        player_service = PlayerService(audio_player)

        observer = MagicMock()
        player_service.attach(observer)

        song = Song(
            title="Song",
            artist="Artist",
            album="Album",
            duration_secs=100.0,
            file_path="/path/to/song.mp3",
        )
        album = Album(title="Album", artist="Artist", songs=[song])

        player_service.load_album(album)
        observer.update.assert_called_with("album_loaded", album)

        player_service.play()
        observer.update.assert_called_with("track_started", song)

        player_service.pause()
        observer.update.assert_called_with("track_paused", song)

        player_service.stop()
        observer.update.assert_called_with("track_stopped", song)

    def test_cartridge_loading(self) -> None:
        """Test loading an album from a cartridge."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test cartridge structure
            cartridge_id = "test_cartridge"
            cartridge_dir = Path(tmpdir) / cartridge_id
            cartridge_dir.mkdir()

            # Create metadata.json
            metadata = {
                "cid": cartridge_id,
                "security_level": "open",
                "version": "1.0",
                "album": {
                    "title": "Test Album",
                    "artist": "Test Artist",
                    "year": 2023,
                    "genre": "Rock",
                    "songs": [
                        {
                            "title": "Song 1",
                            "artist": "Test Artist",
                            "album": "Test Album",
                            "duration_secs": 100.0,
                            "file_path": "song1.mp3",
                            "track_number": 1,
                        },
                        {
                            "title": "Song 2",
                            "artist": "Test Artist",
                            "album": "Test Album",
                            "duration_secs": 200.0,
                            "file_path": "song2.mp3",
                            "track_number": 2,
                        },
                    ],
                },
            }

            import json

            metadata_file = cartridge_dir / "metadata.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f)

            # Create dummy audio files
            (cartridge_dir / "song1.mp3").touch()
            (cartridge_dir / "song2.mp3").touch()

            # Test cartridge reader
            reader = LocalFileCartridgeReader(tmpdir)
            assert reader.is_cartridge_available(cartridge_id)

            cartridge = reader.read_cartridge(cartridge_id)
            assert cartridge is not None
            assert cartridge.cid == cartridge_id

            album = reader.load_album_from_cartridge(cartridge)
            assert album is not None
            assert album.title == "Test Album"
            assert album.artist == "Test Artist"
            assert len(album.songs) == 2
            assert album.songs[0].title == "Song 1"
            assert album.songs[1].title == "Song 2"

            # Test integration with player service
            audio_player = MockAudioPlayer()
            player_service = PlayerService(audio_player)
            player_service.load_album(album)

            assert len(player_service.get_queue()) == 2
            player_service.play()
            assert player_service.get_current_song() == album.songs[0]




