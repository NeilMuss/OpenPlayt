"""Local file cartridge reader implementation."""

import json
from pathlib import Path
from typing import Optional

from ...domain.entities.album import Album
from ...domain.entities.cartridge import Cartridge
from ...domain.entities.song import Song
from ...domain.interfaces.cartridge_reader import CartridgeReaderInterface


class LocalFileCartridgeReader(CartridgeReaderInterface):
    """
    Cartridge reader implementation for local filesystem with JSON metadata.

    This implementation reads cartridges from a directory structure where
    each cartridge is a directory containing:
    - metadata.json: Cartridge and album metadata
    - Audio files referenced in the metadata
    """

    def __init__(self, base_path: str) -> None:
        """
        Initialize the cartridge reader with a base directory.

        Args:
            base_path: Base directory containing cartridge directories
        """
        self._base_path = Path(base_path)
        if not self._base_path.exists():
            raise ValueError(f"Base path does not exist: {base_path}")

    def read_cartridge(self, cartridge_id: str) -> Optional[Cartridge]:
        """Read cartridge metadata by ID."""
        cartridge_path = self._base_path / cartridge_id
        metadata_file = cartridge_path / "metadata.json"

        if not metadata_file.exists():
            return None

        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            return Cartridge(
                cid=metadata.get("cid", cartridge_id),
                security_level=metadata.get("security_level", "open"),
                version=metadata.get("version"),
            )
        except (json.JSONDecodeError, KeyError, IOError):
            return None

    def load_album_from_cartridge(self, cartridge: Cartridge) -> Optional[Album]:
        """Load album data from a cartridge."""
        cartridge_path = self._base_path / cartridge.cid
        metadata_file = cartridge_path / "metadata.json"

        if not metadata_file.exists():
            return None

        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            album_data = metadata.get("album", {})
            songs_data = album_data.get("songs", [])

            songs: list[Song] = []
            for song_data in songs_data:
                # Resolve file path relative to cartridge directory
                file_path = song_data.get("file_path", "")
                if not Path(file_path).is_absolute():
                    file_path = str(cartridge_path / file_path)

                song = Song(
                    title=song_data.get("title", "Unknown"),
                    artist=song_data.get("artist", album_data.get("artist", "Unknown")),
                    album=album_data.get("title", "Unknown"),
                    duration_secs=song_data.get("duration_secs"),
                    file_path=file_path,
                    track_number=song_data.get("track_number"),
                    metadata=song_data.get("metadata", {}),
                )
                songs.append(song)

            album = Album(
                title=album_data.get("title", "Unknown"),
                artist=album_data.get("artist", "Unknown"),
                year=album_data.get("year"),
                genre=album_data.get("genre"),
                songs=songs,
            )

            return album
        except (json.JSONDecodeError, KeyError, IOError):
            return None

    def is_cartridge_available(self, cartridge_id: str) -> bool:
        """Check if a cartridge is available for reading."""
        cartridge_path = self._base_path / cartridge_id
        metadata_file = cartridge_path / "metadata.json"
        return metadata_file.exists()


