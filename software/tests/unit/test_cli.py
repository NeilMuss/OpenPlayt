"""Unit tests for CLI interface."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from playt_player.application.player_service import PlayerService
from playt_player.domain.entities.album import Album
from playt_player.domain.entities.cartridge import Cartridge
from playt_player.domain.entities.song import Song
from playt_player.infrastructure.cartridge.local_file_cartridge_reader import (
    LocalFileCartridgeReader,
)
from playt_player.interface.cli.player_cli import PlayerCLI


class TestPlayerCLI:
    """Test suite for PlayerCLI."""

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

    def test_load_cartridge_with_reader(self, player_service: PlayerService) -> None:
        """Test loading a cartridge when a cartridge reader is provided."""
        # Create a mock cartridge reader
        mock_reader = MagicMock()
        cartridge = Cartridge(cid="test_cartridge", security_level="open")
        album = Album(
            title="Test Album",
            artist="Test Artist",
            songs=[
                Song(
                    title="Song 1",
                    artist="Test Artist",
                    album="Test Album",
                    duration_secs=100.0,
                    file_path="/path/to/song1.mp3",
                    track_number=1,
                )
            ],
        )

        mock_reader.is_cartridge_available.return_value = True
        mock_reader.read_cartridge.return_value = cartridge
        mock_reader.load_album_from_cartridge.return_value = album

        cli = PlayerCLI(player_service, mock_reader)
        cli._load_cartridge("test_cartridge")

        mock_reader.is_cartridge_available.assert_called_once_with("test_cartridge")
        mock_reader.read_cartridge.assert_called_once_with("test_cartridge")
        mock_reader.load_album_from_cartridge.assert_called_once_with(cartridge)
        assert len(player_service.get_queue()) == 1

    def test_load_cartridge_without_reader(self, player_service: PlayerService) -> None:
        """Test loading a cartridge when no cartridge reader is provided."""
        cli = PlayerCLI(player_service, None)

        with patch("builtins.print") as mock_print:
            cli._load_cartridge("test_cartridge")
            mock_print.assert_called_once_with("Cartridge reader not available")

    def test_load_playt_file_creates_reader(
        self, player_service: PlayerService, tmp_path: Path
    ) -> None:
        """Test that loading a .playt file creates a reader if none exists."""
        # Create a mock .playt file (empty zip)
        import zipfile

        playt_file = tmp_path / "test_album.playt"
        with zipfile.ZipFile(playt_file, "w") as zf:
            # Add a dummy audio file entry
            zf.writestr("song1.mp3", b"fake audio data")

        # Mock the PlaytFileCartridgeReader to avoid actual file operations
        # Patch it where it's imported (inside the method)
        with patch(
            "playt_player.infrastructure.cartridge.playt_file_cartridge_reader.PlaytFileCartridgeReader"
        ) as mock_reader_class:
            mock_reader = MagicMock()
            mock_reader_class.return_value = mock_reader

            cartridge = Cartridge(cid="test_album", security_level="open")
            album = Album(
                title="test_album",
                artist="Unknown Artist",
                songs=[
                    Song(
                        title="song1",
                        artist="Unknown Artist",
                        album="test_album",
                        duration_secs=None,
                        file_path=str(tmp_path / "song1.mp3"),
                        track_number=1,
                    )
                ],
            )

            mock_reader.is_cartridge_available.return_value = True
            mock_reader.read_cartridge.return_value = cartridge
            mock_reader.load_album_from_cartridge.return_value = album

            cli = PlayerCLI(player_service, None)
            cli._load_cartridge(str(playt_file))

            # Should have created a PlaytFileCartridgeReader
            mock_reader_class.assert_called_once()
            # Should have used the reader to load the album
            # Note: The path might be resolved to absolute, so check if it was called
            assert mock_reader.is_cartridge_available.called
            assert mock_reader.read_cartridge.called

    def test_load_cartridge_not_found(
        self, player_service: PlayerService
    ) -> None:
        """Test loading a cartridge that doesn't exist."""
        mock_reader = MagicMock()
        mock_reader.is_cartridge_available.return_value = False

        cli = PlayerCLI(player_service, mock_reader)

        with patch("builtins.print") as mock_print:
            cli._load_cartridge("nonexistent_cartridge")
            mock_print.assert_called_once_with(
                "Cartridge not found: nonexistent_cartridge"
            )

    def test_load_cartridge_read_fails(
        self, player_service: PlayerService
    ) -> None:
        """Test loading a cartridge when read fails."""
        mock_reader = MagicMock()
        mock_reader.is_cartridge_available.return_value = True
        mock_reader.read_cartridge.return_value = None

        cli = PlayerCLI(player_service, mock_reader)

        with patch("builtins.print") as mock_print:
            cli._load_cartridge("test_cartridge")
            mock_print.assert_called_once_with(
                "Failed to read cartridge: test_cartridge"
            )

    def test_load_cartridge_load_album_fails(
        self, player_service: PlayerService
    ) -> None:
        """Test loading a cartridge when loading album fails."""
        mock_reader = MagicMock()
        cartridge = Cartridge(cid="test_cartridge", security_level="open")
        mock_reader.is_cartridge_available.return_value = True
        mock_reader.read_cartridge.return_value = cartridge
        mock_reader.load_album_from_cartridge.return_value = None

        cli = PlayerCLI(player_service, mock_reader)

        with patch("builtins.print") as mock_print:
            cli._load_cartridge("test_cartridge")
            mock_print.assert_called_once_with(
                "Failed to load album from cartridge: test_cartridge"
            )

    def test_show_status_with_song(self, player_service: PlayerService) -> None:
        """Test showing status when a song is loaded."""
        song = Song(
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            duration_secs=100.0,
            file_path="/path/to/song.mp3",
        )
        album = Album(title="Test Album", artist="Test Artist", songs=[song])
        player_service.load_album(album)
        player_service.play()

        cli = PlayerCLI(player_service)
        with patch("builtins.print") as mock_print:
            cli._show_status()
            # Should print status information
            assert mock_print.called
            call_args = str(mock_print.call_args)
            assert "State:" in call_args or "Song:" in call_args

    def test_show_status_without_song(self, player_service: PlayerService) -> None:
        """Test showing status when no song is loaded."""
        cli = PlayerCLI(player_service)
        with patch("builtins.print") as mock_print:
            cli._show_status()
            # Should print status information
            assert mock_print.called
            call_args = str(mock_print.call_args)
            assert "State:" in call_args or "No song loaded" in call_args

    def test_load_playt_file_with_relative_path(
        self, player_service: PlayerService, tmp_path: Path, monkeypatch
    ) -> None:
        """Test that loading a .playt file with a relative path works in interactive mode."""
        import zipfile

        # Change to tmp_path directory
        monkeypatch.chdir(tmp_path)

        playt_file = tmp_path / "test_album.playt"
        with zipfile.ZipFile(playt_file, "w") as zf:
            zf.writestr("song1.mp3", b"fake audio data")

        # Mock the PlaytFileCartridgeReader
        with patch(
            "playt_player.infrastructure.cartridge.playt_file_cartridge_reader.PlaytFileCartridgeReader"
        ) as mock_reader_class:
            mock_reader = MagicMock()
            mock_reader_class.return_value = mock_reader

            cartridge = Cartridge(cid="test_album", security_level="open")
            album = Album(
                title="test_album",
                artist="Unknown Artist",
                songs=[
                    Song(
                        title="song1",
                        artist="Unknown Artist",
                        album="test_album",
                        duration_secs=None,
                        file_path=str(tmp_path / "song1.mp3"),
                        track_number=1,
                    )
                ],
            )

            mock_reader.is_cartridge_available.return_value = True
            mock_reader.read_cartridge.return_value = cartridge
            mock_reader.load_album_from_cartridge.return_value = album

            # Start CLI without a reader (simulating interactive mode)
            cli = PlayerCLI(player_service, None)

            # Load with relative path
            cli._load_cartridge("test_album.playt")

            # Should have created a PlaytFileCartridgeReader
            mock_reader_class.assert_called_once()
            # Should have resolved the path and used it
            assert mock_reader.is_cartridge_available.called

