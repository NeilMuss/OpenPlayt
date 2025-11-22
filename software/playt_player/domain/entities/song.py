"""Song domain entity representing a single audio track."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class Song:
    """
    Represents a single audio track.

    Attributes:
        title: The title of the song
        artist: The artist/band name
        album: The album name this song belongs to
        duration_secs: Duration in seconds (None if unknown)
        file_path: Path to the audio file
        track_number: Track number on the album (None if unknown)
        metadata: Additional metadata as a dictionary
    """

    title: str
    artist: str
    album: str
    duration_secs: Optional[float]
    file_path: str
    track_number: Optional[int] = None
    cover_art_path: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize default metadata if not provided."""
        # default_factory handles initialization
        pass

    def __repr__(self) -> str:
        """String representation of the song."""
        track_str = f"#{self.track_number}" if self.track_number else "?"
        duration_str = f"{self.duration_secs:.1f}s" if self.duration_secs else "?"
        return (
            f"Song(title='{self.title}', artist='{self.artist}', "
            f"album='{self.album}', track={track_str}, duration={duration_str})"
        )

    def __eq__(self, other: object) -> bool:
        """Equality comparison based on file_path."""
        if not isinstance(other, Song):
            return False
        return self.file_path == other.file_path

    def __hash__(self) -> int:
        """Hash based on file_path for use in sets/dicts."""
        return hash(self.file_path)
