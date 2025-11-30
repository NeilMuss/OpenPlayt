"""Unit tests for Album entity."""

import pytest

from playt_player.domain.entities.album import Album
from playt_player.domain.entities.song import Song


class TestAlbum:
    """Test suite for Album entity."""

    def test_album_creation(self) -> None:
        """Test creating an album with all fields."""
        album = Album(
            title="Test Album",
            artist="Test Artist",
            year=2023,
            genre="Rock",
            songs=[],
        )

        assert album.title == "Test Album"
        assert album.artist == "Test Artist"
        assert album.year == 2023
        assert album.genre == "Rock"
        assert album.songs == []

    def test_album_creation_minimal(self) -> None:
        """Test creating an album with minimal fields."""
        album = Album(title="Minimal Album", artist="Minimal Artist")

        assert album.title == "Minimal Album"
        assert album.artist == "Minimal Artist"
        assert album.year is None
        assert album.genre is None
        assert album.songs == []

    def test_album_equality(self) -> None:
        """Test album equality based on title and artist."""
        album1 = Album(title="Album", artist="Artist", year=2020)
        album2 = Album(title="Album", artist="Artist", year=2023)  # Different year
        album3 = Album(title="Other Album", artist="Artist")  # Different title

        assert album1 == album2  # Same title and artist
        assert album1 != album3  # Different title
        assert album1 != "not an album"  # Different type

    def test_ordered_songs(self) -> None:
        """Test ordering songs by track number."""
        song1 = Song(
            title="Song 1",
            artist="Artist",
            album="Album",
            duration_secs=100.0,
            file_path="/path/to/1.mp3",
            track_number=3,
        )
        song2 = Song(
            title="Song 2",
            artist="Artist",
            album="Album",
            duration_secs=200.0,
            file_path="/path/to/2.mp3",
            track_number=1,
        )
        song3 = Song(
            title="Song 3",
            artist="Artist",
            album="Album",
            duration_secs=300.0,
            file_path="/path/to/3.mp3",
            track_number=2,
        )
        song4 = Song(
            title="Song 4",
            artist="Artist",
            album="Album",
            duration_secs=400.0,
            file_path="/path/to/4.mp3",
            track_number=None,
        )

        album = Album(title="Album", artist="Artist", songs=[song1, song2, song3, song4])
        ordered = album.ordered_songs()

        assert ordered[0] == song2  # Track 1
        assert ordered[1] == song3  # Track 2
        assert ordered[2] == song1  # Track 3
        assert ordered[3] == song4  # No track number (sorted last)

    def test_total_duration(self) -> None:
        """Test calculating total album duration."""
        song1 = Song(
            title="Song 1",
            artist="Artist",
            album="Album",
            duration_secs=100.0,
            file_path="/path/to/1.mp3",
        )
        song2 = Song(
            title="Song 2",
            artist="Artist",
            album="Album",
            duration_secs=200.0,
            file_path="/path/to/2.mp3",
        )

        album = Album(title="Album", artist="Artist", songs=[song1, song2])
        assert album.total_duration() == 300.0

    def test_total_duration_with_none(self) -> None:
        """Test total duration when some songs have unknown duration."""
        song1 = Song(
            title="Song 1",
            artist="Artist",
            album="Album",
            duration_secs=100.0,
            file_path="/path/to/1.mp3",
        )
        song2 = Song(
            title="Song 2",
            artist="Artist",
            album="Album",
            duration_secs=None,
            file_path="/path/to/2.mp3",
        )

        album = Album(title="Album", artist="Artist", songs=[song1, song2])
        assert album.total_duration() is None

    def test_total_duration_empty_album(self) -> None:
        """Test total duration of empty album."""
        album = Album(title="Album", artist="Artist", songs=[])
        assert album.total_duration() == 0.0

    def test_album_repr(self) -> None:
        """Test string representation of album."""
        album = Album(title="Test Album", artist="Test Artist", year=2023)
        repr_str = repr(album)

        assert "Test Album" in repr_str
        assert "Test Artist" in repr_str
        assert "2023" in repr_str






