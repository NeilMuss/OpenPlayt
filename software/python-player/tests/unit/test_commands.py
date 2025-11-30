"""Unit tests for command pattern implementations."""

from unittest.mock import MagicMock

import pytest

from playt_player.application.commands.next_command import NextCommand
from playt_player.application.commands.pause_command import PauseCommand
from playt_player.application.commands.play_command import PlayCommand
from playt_player.application.commands.prev_command import PrevCommand
from playt_player.application.commands.stop_command import StopCommand
from playt_player.application.player_service import PlayerService


class TestCommands:
    """Test suite for command implementations."""

    @pytest.fixture
    def mock_audio_player(self) -> MagicMock:
        """Create a mock audio player."""
        player = MagicMock()
        player.is_playing.return_value = False
        player.get_state.return_value = "idle"
        return player

    @pytest.fixture
    def player_service(self, mock_audio_player: MagicMock) -> PlayerService:
        """Create a player service with mock audio player."""
        return PlayerService(mock_audio_player)

    def test_play_command(self, player_service: PlayerService) -> None:
        """Test play command execution."""
        from playt_player.domain.entities.album import Album
        from playt_player.domain.entities.song import Song

        song = Song(
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            duration_secs=100.0,
            file_path="/path/to/song.mp3",
        )
        album = Album(title="Test Album", artist="Test Artist", songs=[song])
        player_service.load_album(album)

        command = PlayCommand(player_service)
        command.execute()

        player_service._audio_player.play.assert_called_once_with("/path/to/song.mp3")

    def test_pause_command(self, player_service: PlayerService, mock_audio_player: MagicMock) -> None:
        """Test pause command execution."""
        mock_audio_player.is_playing.return_value = True

        command = PauseCommand(player_service)
        command.execute()

        player_service._audio_player.pause.assert_called_once()

    def test_stop_command(self, player_service: PlayerService) -> None:
        """Test stop command execution."""
        command = StopCommand(player_service)
        command.execute()

        player_service._audio_player.stop.assert_called_once()

    def test_next_command(self, player_service: PlayerService) -> None:
        """Test next command execution."""
        from playt_player.domain.entities.album import Album
        from playt_player.domain.entities.song import Song

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
        player_service.play()  # Start playing first song

        command = NextCommand(player_service)
        command.execute()

        # Should have called play with second song
        assert player_service._audio_player.play.call_count >= 2
        player_service._audio_player.play.assert_called_with("/path/to/2.mp3")

    def test_prev_command(self, player_service: PlayerService) -> None:
        """Test previous command execution."""
        from playt_player.domain.entities.album import Album
        from playt_player.domain.entities.song import Song

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
        player_service.play()  # Start playing first song
        player_service.next()  # Move to second song

        command = PrevCommand(player_service)
        command.execute()

        # Should have called play with first song
        player_service._audio_player.play.assert_called_with("/path/to/1.mp3")






