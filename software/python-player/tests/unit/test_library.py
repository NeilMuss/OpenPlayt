"""Unit tests for Library entity."""

import pytest

from playt_player.domain.entities.album import Album
from playt_player.domain.entities.library import Library
from playt_player.domain.entities.song import Song


class TestLibrary:
    """Test suite for Library entity."""

    def test_library_creation(self) -> None:
        """Test creating an empty library."""
        library = Library()
        assert library.albums == []
        assert len(library.get_all_songs()) == 0

    def test_add_album(self) -> None:
        """Test adding an album to the library."""
        library = Library()
        song = Song(
            title="Song",
            artist="Artist",
            album="Album",
            duration_secs=100.0,
            file_path="/path/to/song.mp3",
        )
        album = Album(title="Album", artist="Artist", songs=[song])

        library.add_album(album)

        assert len(library.albums) == 1
        assert library.albums[0] == album
        assert len(library.get_all_songs()) == 1

    def test_add_duplicate_album(self) -> None:
        """Test that adding the same album twice doesn't duplicate it."""
        library = Library()
        album = Album(title="Album", artist="Artist", songs=[])

        library.add_album(album)
        library.add_album(album)

        assert len(library.albums) == 1

    def test_remove_album(self) -> None:
        """Test removing an album from the library."""
        library = Library()
        album1 = Album(title="Album 1", artist="Artist", songs=[])
        album2 = Album(title="Album 2", artist="Artist", songs=[])

        library.add_album(album1)
        library.add_album(album2)
        library.remove_album(album1)

        assert len(library.albums) == 1
        assert library.albums[0] == album2

    def test_find_song_by_path(self) -> None:
        """Test finding a song by file path."""
        library = Library()
        song = Song(
            title="Song",
            artist="Artist",
            album="Album",
            duration_secs=100.0,
            file_path="/path/to/song.mp3",
        )
        album = Album(title="Album", artist="Artist", songs=[song])
        library.add_album(album)

        found = library.find_song_by_path("/path/to/song.mp3")
        assert found == song

        not_found = library.find_song_by_path("/path/to/other.mp3")
        assert not_found is None

    def test_find_album(self) -> None:
        """Test finding an album by title and artist."""
        library = Library()
        album = Album(title="Album", artist="Artist", songs=[])
        library.add_album(album)

        found = library.find_album("Album", "Artist")
        assert found == album

        not_found = library.find_album("Other Album", "Artist")
        assert not_found is None

    def test_search_songs(self) -> None:
        """Test searching for songs by query."""
        library = Library()
        song1 = Song(
            title="Rock Song",
            artist="Rock Artist",
            album="Rock Album",
            duration_secs=100.0,
            file_path="/path/to/rock.mp3",
        )
        song2 = Song(
            title="Jazz Song",
            artist="Jazz Artist",
            album="Jazz Album",
            duration_secs=200.0,
            file_path="/path/to/jazz.mp3",
        )
        album = Album(title="Mixed Album", artist="Various", songs=[song1, song2])
        library.add_album(album)

        results = library.search_songs("Rock")
        assert len(results) == 1
        assert results[0] == song1

        results = library.search_songs("Jazz")
        assert len(results) == 1
        assert results[0] == song2

        results = library.search_songs("Song")
        assert len(results) == 2

        results = library.search_songs("Nonexistent")
        assert len(results) == 0

    def test_search_songs_case_insensitive(self) -> None:
        """Test that search is case-insensitive."""
        library = Library()
        song = Song(
            title="Rock Song",
            artist="Rock Artist",
            album="Rock Album",
            duration_secs=100.0,
            file_path="/path/to/rock.mp3",
        )
        album = Album(title="Album", artist="Artist", songs=[song])
        library.add_album(album)

        results = library.search_songs("rock")
        assert len(results) == 1

        results = library.search_songs("ROCK")
        assert len(results) == 1

    def test_get_all_songs(self) -> None:
        """Test getting all songs from all albums."""
        library = Library()
        song1 = Song(
            title="Song 1",
            artist="Artist",
            album="Album 1",
            duration_secs=100.0,
            file_path="/path/to/1.mp3",
        )
        song2 = Song(
            title="Song 2",
            artist="Artist",
            album="Album 2",
            duration_secs=200.0,
            file_path="/path/to/2.mp3",
        )
        album1 = Album(title="Album 1", artist="Artist", songs=[song1])
        album2 = Album(title="Album 2", artist="Artist", songs=[song2])

        library.add_album(album1)
        library.add_album(album2)

        all_songs = library.get_all_songs()
        assert len(all_songs) == 2
        assert song1 in all_songs
        assert song2 in all_songs






