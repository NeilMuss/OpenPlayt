"""Unit tests for PlayerService."""

from unittest.mock import MagicMock

import pytest

from playt_player.application.player_service import PlayerService
from playt_player.domain.entities.album import Album
from playt_player.domain.entities.song import Song
from playt_player.domain.interfaces.observer import Observer


class TestPlayerService:
    """Test suite for PlayerService."""

    @pytest.fixture
    def mock_audio_player(self) -> MagicMock:
        """Create a mock audio player."""
        player = MagicMock()
        player.is_playing.return_value = False
        player.get_state.return_value = "idle"
        player.get_position.return_value = None
        return player

    @pytest.fixture
    def player_service(self, mock_audio_player: MagicMock) -> PlayerService:
        """Create a player service with mock audio player."""
        return PlayerService(mock_audio_player)

    def test_load_album(self, player_service: PlayerService) -> None:
        """Test loading an album into the queue."""
        song = Song(
            title="Song",
            artist="Artist",
            album="Album",
            duration_secs=100.0,
            file_path="/path/to/song.mp3",
        )
        album = Album(title="Album", artist="Artist", songs=[song])

        observer = MagicMock(spec=Observer)
        player_service.attach(observer)

        player_service.load_album(album)

        assert len(player_service.get_queue()) == 1
        observer.update.assert_called_with("album_loaded", album)

    def test_play(self, player_service: PlayerService) -> None:
        """Test starting playback."""
        song = Song(
            title="Song",
            artist="Artist",
            album="Album",
            duration_secs=100.0,
            file_path="/path/to/song.mp3",
        )
        album = Album(title="Album", artist="Artist", songs=[song])
        player_service.load_album(album)

        observer = MagicMock(spec=Observer)
        player_service.attach(observer)

        player_service.play()

        player_service._audio_player.play.assert_called_once_with("/path/to/song.mp3")
        observer.update.assert_called_with("track_started", song)
        assert player_service.get_current_song() == song

    def test_pause(self, player_service: PlayerService, mock_audio_player: MagicMock) -> None:
        """Test pausing playback."""
        mock_audio_player.is_playing.return_value = True
        song = Song(
            title="Song",
            artist="Artist",
            album="Album",
            duration_secs=100.0,
            file_path="/path/to/song.mp3",
        )
        album = Album(title="Album", artist="Artist", songs=[song])
        player_service.load_album(album)
        player_service.play()

        observer = MagicMock(spec=Observer)
        player_service.attach(observer)

        player_service.pause()

        player_service._audio_player.pause.assert_called_once()
        observer.update.assert_called_with("track_paused", song)

    def test_stop(self, player_service: PlayerService) -> None:
        """Test stopping playback."""
        song = Song(
            title="Song",
            artist="Artist",
            album="Album",
            duration_secs=100.0,
            file_path="/path/to/song.mp3",
        )
        album = Album(title="Album", artist="Artist", songs=[song])
        player_service.load_album(album)
        player_service.play()

        observer = MagicMock(spec=Observer)
        player_service.attach(observer)

        player_service.stop()

        player_service._audio_player.stop.assert_called_once()
        observer.update.assert_called_with("track_stopped", song)
        assert player_service.get_current_song() is None

    def test_next(self, player_service: PlayerService) -> None:
        """Test skipping to next track."""
        song1 = Song(
            title="Song 1",
            artist="Artist",
            album="Album",
            duration_secs=100.0,
            file_path="/path/to/1.mp3",
            track_number=1,
        )
        song2 = Song(
            title="Song 2",
            artist="Artist",
            album="Album",
            duration_secs=200.0,
            file_path="/path/to/2.mp3",
            track_number=2,
        )
        album = Album(title="Album", artist="Artist", songs=[song1, song2])
        player_service.load_album(album)
        player_service.play()

        observer = MagicMock(spec=Observer)
        player_service.attach(observer)

        player_service.next()

        player_service._audio_player.play.assert_called_with("/path/to/2.mp3")
        observer.update.assert_called_with("track_started", song2)
        assert player_service.get_current_song() == song2

    def test_previous(self, player_service: PlayerService) -> None:
        """Test going to previous track."""
        song1 = Song(
            title="Song 1",
            artist="Artist",
            album="Album",
            duration_secs=100.0,
            file_path="/path/to/1.mp3",
            track_number=1,
        )
        song2 = Song(
            title="Song 2",
            artist="Artist",
            album="Album",
            duration_secs=200.0,
            file_path="/path/to/2.mp3",
            track_number=2,
        )
        album = Album(title="Album", artist="Artist", songs=[song1, song2])
        player_service.load_album(album)
        player_service.play()
        player_service.next()

        observer = MagicMock(spec=Observer)
        player_service.attach(observer)

        player_service.previous()

        player_service._audio_player.play.assert_called_with("/path/to/1.mp3")
        observer.update.assert_called_with("track_started", song1)
        assert player_service.get_current_song() == song1

    def test_seek(self, player_service: PlayerService) -> None:
        """Test seeking to a position."""
        song = Song(
            title="Song",
            artist="Artist",
            album="Album",
            duration_secs=100.0,
            file_path="/path/to/song.mp3",
        )
        album = Album(title="Album", artist="Artist", songs=[song])
        player_service.load_album(album)
        player_service.play()

        observer = MagicMock(spec=Observer)
        player_service.attach(observer)

        player_service.seek(50.0)

        player_service._audio_player.seek.assert_called_once_with(50.0)
        observer.update.assert_called()
        call_args = observer.update.call_args[0]
        assert call_args[0] == "seeked"
        assert call_args[1]["position"] == 50.0





