"""Unit tests for Song entity."""

import pytest

from playt_player.domain.entities.song import Song


class TestSong:
    """Test suite for Song entity."""

    def test_song_creation(self) -> None:
        """Test creating a song with all fields."""
        song = Song(
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            duration_secs=180.5,
            file_path="/path/to/song.mp3",
            track_number=1,
            metadata={"genre": "Rock"},
        )

        assert song.title == "Test Song"
        assert song.artist == "Test Artist"
        assert song.album == "Test Album"
        assert song.duration_secs == 180.5
        assert song.file_path == "/path/to/song.mp3"
        assert song.track_number == 1
        assert song.metadata == {"genre": "Rock"}

    def test_song_creation_minimal(self) -> None:
        """Test creating a song with minimal required fields."""
        song = Song(
            title="Minimal Song",
            artist="Minimal Artist",
            album="Minimal Album",
            duration_secs=None,
            file_path="/path/to/minimal.mp3",
        )

        assert song.title == "Minimal Song"
        assert song.track_number is None
        assert song.duration_secs is None
        assert song.metadata == {}

    def test_song_equality(self) -> None:
        """Test song equality based on file_path."""
        song1 = Song(
            title="Song 1",
            artist="Artist",
            album="Album",
            duration_secs=100.0,
            file_path="/path/to/song.mp3",
        )
        song2 = Song(
            title="Song 2",  # Different title
            artist="Artist",
            album="Album",
            duration_secs=200.0,  # Different duration
            file_path="/path/to/song.mp3",  # Same path
        )
        song3 = Song(
            title="Song 1",
            artist="Artist",
            album="Album",
            duration_secs=100.0,
            file_path="/path/to/other.mp3",  # Different path
        )

        assert song1 == song2  # Same file_path
        assert song1 != song3  # Different file_path
        assert song1 != "not a song"  # Different type

    def test_song_hash(self) -> None:
        """Test song hashing for use in sets/dicts."""
        song1 = Song(
            title="Song 1",
            artist="Artist",
            album="Album",
            duration_secs=100.0,
            file_path="/path/to/song.mp3",
        )
        song2 = Song(
            title="Song 2",
            artist="Artist",
            album="Album",
            duration_secs=200.0,
            file_path="/path/to/song.mp3",  # Same path
        )

        song_set = {song1, song2}
        assert len(song_set) == 1  # Same hash due to same file_path

    def test_song_repr(self) -> None:
        """Test string representation of song."""
        song = Song(
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            duration_secs=180.5,
            file_path="/path/to/song.mp3",
            track_number=5,
        )

        repr_str = repr(song)
        assert "Test Song" in repr_str
        assert "Test Artist" in repr_str
        assert "#5" in repr_str
        assert "180.5s" in repr_str

    def test_song_repr_with_none_values(self) -> None:
        """Test string representation with None values."""
        song = Song(
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            duration_secs=None,
            file_path="/path/to/song.mp3",
            track_number=None,
        )

        repr_str = repr(song)
        assert "?" in repr_str  # Should show ? for unknown values





