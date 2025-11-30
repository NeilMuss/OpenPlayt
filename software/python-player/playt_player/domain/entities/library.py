"""Library domain entity for indexing and managing collections of albums."""

from dataclasses import dataclass, field
from typing import Optional

from .album import Album
from .song import Song


@dataclass
class Library:
    """
    Manages a collection of albums with indexing and search capabilities.

    Attributes:
        albums: List of albums in the library
        _song_index: Internal index mapping file paths to songs
        _album_index: Internal index mapping (title, artist) to albums
    """

    albums: list[Album] = field(default_factory=list)
    _song_index: dict[str, Song] = field(default_factory=dict, init=False, repr=False)
    _album_index: dict[tuple[str, str], Album] = field(
        default_factory=dict, init=False, repr=False
    )

    def __post_init__(self) -> None:
        """Build internal indexes after initialization."""
        self._rebuild_indexes()

    def __repr__(self) -> str:
        """String representation of the library."""
        album_count = len(self.albums)
        song_count = sum(len(album.songs) for album in self.albums)
        return f"Library(albums={album_count}, songs={song_count})"

    def add_album(self, album: Album) -> None:
        """
        Add an album to the library and update indexes.

        Args:
            album: The album to add
        """
        if album not in self.albums:
            self.albums.append(album)
            self._update_indexes_for_album(album)

    def remove_album(self, album: Album) -> None:
        """
        Remove an album from the library and update indexes.

        Args:
            album: The album to remove
        """
        if album in self.albums:
            self.albums.remove(album)
            self._rebuild_indexes()

    def find_song_by_path(self, file_path: str) -> Optional[Song]:
        """
        Find a song by its file path.

        Args:
            file_path: Path to the audio file

        Returns:
            Song if found, None otherwise
        """
        return self._song_index.get(file_path)

    def find_album(self, title: str, artist: str) -> Optional[Album]:
        """
        Find an album by title and artist.

        Args:
            title: Album title
            artist: Artist name

        Returns:
            Album if found, None otherwise
        """
        return self._album_index.get((title, artist))

    def search_songs(self, query: str) -> list[Song]:
        """
        Search for songs by title, artist, or album name.

        Args:
            query: Search query (case-insensitive)

        Returns:
            List of matching songs
        """
        query_lower = query.lower()
        results: list[Song] = []
        for song in self._song_index.values():
            if (
                query_lower in song.title.lower()
                or query_lower in song.artist.lower()
                or query_lower in song.album.lower()
            ):
                results.append(song)
        return results

    def get_all_songs(self) -> list[Song]:
        """
        Get all songs from all albums.

        Returns:
            List of all songs in the library
        """
        return list(self._song_index.values())

    def _rebuild_indexes(self) -> None:
        """Rebuild all internal indexes from scratch."""
        self._song_index.clear()
        self._album_index.clear()
        for album in self.albums:
            self._update_indexes_for_album(album)

    def _update_indexes_for_album(self, album: Album) -> None:
        """Update indexes for a single album."""
        self._album_index[(album.title, album.artist)] = album
        for song in album.songs:
            self._song_index[song.file_path] = song


