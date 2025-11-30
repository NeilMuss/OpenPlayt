"""Album domain entity representing a collection of songs."""

from dataclasses import dataclass, field
from typing import Optional

from .song import Song


@dataclass
class Album:
    """
    Represents a collection of songs forming an album.

    Attributes:
        title: The album title
        artist: The artist/band name
        year: Release year (None if unknown)
        genre: Genre classification (None if unknown)
        songs: List of songs in this album
    """

    title: str
    artist: str
    year: Optional[int] = None
    genre: Optional[str] = None
    cover_art_path: Optional[str] = None
    slideshow_images: list[str] = field(default_factory=list)
    songs: list[Song] = field(default_factory=list)

    def __repr__(self) -> str:
        """String representation of the album."""
        year_str = str(self.year) if self.year else "?"
        song_count = len(self.songs)
        return (
            f"Album(title='{self.title}', artist='{self.artist}', "
            f"year={year_str}, songs={song_count})"
        )

    def __eq__(self, other: object) -> bool:
        """Equality comparison based on title and artist."""
        if not isinstance(other, Album):
            return False
        return self.title == other.title and self.artist == other.artist

    def ordered_songs(self) -> list[Song]:
        """
        Return songs ordered by track number, then by title.

        Returns:
            List of songs sorted by track number (unknown tracks last)
        """
        return sorted(
            self.songs, key=lambda s: (s.track_number if s.track_number is not None else 999, s.title)
        )

    def total_duration(self) -> Optional[float]:
        """
        Calculate total duration of all songs in the album.

        Returns:
            Total duration in seconds, or None if any song duration is unknown
        """
        if not self.songs:
            return 0.0
        durations = [s.duration_secs for s in self.songs if s.duration_secs is not None]
        if len(durations) != len(self.songs):
            return None
        return sum(durations)


