"""Integration test for loading the provided .playt cartridge."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from playt_player.application.player_service import PlayerService
from playt_player.domain.interfaces.audio_player import AudioPlayerInterface
from playt_player.infrastructure.cartridge.playt_file_cartridge_reader import (
    PlaytFileCartridgeReader,
)

REAL_CARTRIDGE_PATH = Path("/Users/neilmussett/Downloads/TheSpells-TheNightHasEyes.playt")


@pytest.mark.skipif(
    not REAL_CARTRIDGE_PATH.exists(),
    reason=f"Cartridge not found at {REAL_CARTRIDGE_PATH}",
)
def test_load_real_cartridge_and_queue_tracks() -> None:
    """Ensure we can load and queue the provided .playt cartridge."""
    reader = PlaytFileCartridgeReader()
    cartridge = reader.read_cartridge(str(REAL_CARTRIDGE_PATH))
    assert cartridge is not None, "Failed to read cartridge metadata"

    album = reader.load_album_from_cartridge(cartridge)
    assert album is not None, "Failed to parse album data"
    assert album.songs, "Album contained no songs"

    mock_audio = MagicMock(spec=AudioPlayerInterface)
    mock_audio.is_playing.return_value = False
    mock_audio.get_state.return_value = "idle"
    mock_audio.get_position.return_value = None

    service = PlayerService(mock_audio)
    service.load_album(album)
    service.play()

    first_song_path = album.ordered_songs()[0].file_path
    mock_audio.play.assert_called_once_with(first_song_path)

