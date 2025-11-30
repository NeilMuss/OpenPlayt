"""Playt file cartridge reader implementation for .playt zip files."""

import shutil
import subprocess
import tempfile
import zipfile
import re
import unicodedata
from pathlib import Path
from typing import Optional

from ...domain.entities.album import Album
from ...domain.entities.cartridge import Cartridge
from ...domain.entities.song import Song
from ...domain.interfaces.cartridge_reader import CartridgeReaderInterface


class PlaytFileCartridgeReader(CartridgeReaderInterface):
    """
    Cartridge reader implementation for .playt zip files.

    This implementation:
    1. Extracts .playt zip files to a temporary directory
    2. Finds all audio files in the top-level folder
    3. Creates an album with those songs
    """

    # Supported audio file extensions
    AUDIO_EXTENSIONS = {".mp3", ".flac", ".wav", ".m4a", ".aac", ".ogg", ".opus"}
    # Supported image file extensions
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

    def __init__(self) -> None:
        """Initialize the playt file cartridge reader."""
        self._temp_dirs: dict[str, Path] = {}  # Track temp dirs for cleanup
        self._file_paths: dict[str, str] = {}  # Map cartridge IDs to file paths

    def read_cartridge(self, cartridge_id: str) -> Optional[Cartridge]:
        """
        Read cartridge metadata from a .playt file path.

        Args:
            cartridge_id: Path to the .playt file

        Returns:
            Cartridge object if the file exists and is valid, None otherwise
        """
        playt_path = Path(cartridge_id)
        if not playt_path.exists() or not playt_path.suffix.lower() == ".playt":
            return None

        try:
            # Verify it's a valid zip file
            with zipfile.ZipFile(playt_path, "r") as zip_ref:
                # Get the first entry to determine structure
                if not zip_ref.namelist():
                    return None

            # Use file name as cartridge ID
            cid = playt_path.stem
            # Store the full file path for later use
            self._file_paths[cid] = str(playt_path.absolute())
            return Cartridge(
                cid=cid,
                security_level="open",
                version=None,
            )
        except (zipfile.BadZipFile, IOError):
            return None

    def _clean_title(self, title: str) -> str:
        """Remove leading track numbers from title and normalize."""
        # Remove leading digits and separators
        title = re.sub(r"^\d+[\s\.\-_]+", "", title)
        # Normalize unicode characters to NFC (composed) form
        return unicodedata.normalize("NFC", title)

    def _get_duration(self, file_path: Path) -> Optional[float]:
        """Get duration of audio file using ffprobe."""
        try:
            # ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp3
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(file_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except (subprocess.SubprocessError, ValueError):
            return None

    def _parse_metadata(
        self, filename: str, default_album: str
    ) -> tuple[str, str, str]:
        """
        Parse metadata from filename.

        Convention: Artist - Album - Song

        Args:
            filename: Filename without extension
            default_album: Default album name to use if not parsed

        Returns:
            Tuple of (title, artist, album)
        """
        parts = filename.split(" - ")
        
        if len(parts) >= 3:
            artist = parts[0]
            album = parts[1]
            title = " - ".join(parts[2:])
            return (
                self._clean_title(title),
                unicodedata.normalize("NFC", artist),
                unicodedata.normalize("NFC", album),
            )
        elif len(parts) == 2:
            # Assuming Artist - Song
            artist = parts[0]
            title = parts[1]
            return (
                self._clean_title(title),
                unicodedata.normalize("NFC", artist),
                unicodedata.normalize("NFC", default_album),
            )
        else:
            return (
                self._clean_title(filename),
                "Unknown Artist",
                unicodedata.normalize("NFC", default_album),
            )

    def _find_cover_art(self, directory: Path) -> tuple[Optional[str], list[str]]:
        """
        Find cover art and slideshow images in the directory.
        
        Returns:
            Tuple of (cover_art_path, slideshow_image_paths)
        """
        if not directory.is_dir():
            return None, []
            
        images = []
        for item in directory.iterdir():
            if item.is_file() and item.suffix.lower() in self.IMAGE_EXTENSIONS:
                images.append(item)
                
        if not images:
            return None, []
            
        cover_art_path = None
        
        # Priority search for cover art
        priority_names = ["cover", "folder", "front", "album"]
        for name in priority_names:
            for img in images:
                if img.stem.lower() == name:
                    cover_art_path = str(img)
                    break
            if cover_art_path:
                break
                    
        # Fallback to first image found if no priority match
        if not cover_art_path and images:
            cover_art_path = str(images[0])
            
        # Filter slideshow images
        slideshow_images = []
        excluded_terms = ["cover"] # User said "not named anything like 'cover'"
        
        for img in images:
            img_path = str(img)
            # Skip the selected cover art
            if img_path == cover_art_path:
                continue
                
            # Skip files containing 'cover' in the name (case insensitive)
            if "cover" in img.stem.lower():
                continue
                
            slideshow_images.append(img_path)
            
        return cover_art_path, sorted(slideshow_images)

    def load_album_from_cartridge(self, cartridge: Cartridge) -> Optional[Album]:
        """
        Load album data from a .playt file.

        Extracts the zip file and finds all audio files in the top-level folder.

        Args:
            cartridge: The cartridge object (cartridge.cid is the cartridge ID)

        Returns:
            Album object if successfully loaded, None otherwise
        """
        # Get the file path from the stored mapping
        if cartridge.cid not in self._file_paths:
            return None

        playt_path = Path(self._file_paths[cartridge.cid])
        if not playt_path.exists() or playt_path.suffix.lower() != ".playt":
            return None

        try:
            # Extract to temporary directory
            temp_dir = tempfile.mkdtemp(prefix="playt_")
            self._temp_dirs[cartridge.cid] = Path(temp_dir)

            with zipfile.ZipFile(playt_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            # Find all audio files in the top-level folder
            # Check if there's a single subdirectory (common zip pattern)
            top_level_dir = Path(temp_dir)
            audio_files = self._find_audio_files(top_level_dir)
            content_dir = top_level_dir

            # If no files found at root, look through subdirectories
            if not audio_files:
                subdirs = [d for d in top_level_dir.iterdir() if d.is_dir()]
                for subdir in subdirs:
                    # Ignore macOS resource directories
                    if subdir.name.startswith("__MACOSX"):
                        continue
                    candidate_files = self._find_audio_files(subdir)
                    if candidate_files:
                        audio_files = candidate_files
                        content_dir = subdir
                        break

            if not audio_files:
                # Clean up temp directory if no audio files found
                shutil.rmtree(temp_dir)
                return None

            # Find cover art and slideshow images in the same directory as content
            cover_art_path, slideshow_images = self._find_cover_art(content_dir)

            # Create songs from audio files
            songs: list[Song] = []
            
            # Track potential album metadata
            artists = set()
            albums = set()
            
            for idx, audio_file in enumerate(sorted(audio_files), start=1):
                # Get filename without extension for title
                filename_stem = audio_file.stem
                
                title, artist, album_name = self._parse_metadata(
                    filename_stem, cartridge.cid
                )
                
                if artist != "Unknown Artist":
                    artists.add(artist)
                albums.add(album_name)

                # Create song - file_path will be absolute path to extracted file
                song = Song(
                    title=title,
                    artist=artist,
                    album=album_name,
                    duration_secs=self._get_duration(audio_file),
                    file_path=str(audio_file),
                    track_number=idx,
                    cover_art_path=cover_art_path,
                    slideshow_images=slideshow_images,
                    metadata={},
                )
                songs.append(song)

            # Determine album artist and title
            album_artist = "Unknown Artist"
            if len(artists) == 1:
                album_artist = list(artists)[0]
            elif len(artists) > 1:
                album_artist = "Various Artists"
                
            album_title = cartridge.cid
            if len(albums) == 1:
                album_title = list(albums)[0]

            # Create album
            album = Album(
                title=album_title,
                artist=album_artist,
                year=None,
                genre=None,
                cover_art_path=cover_art_path,
                slideshow_images=slideshow_images,
                songs=songs,
            )

            return album
        except (zipfile.BadZipFile, IOError, OSError) as e:
            # Clean up on error
            if cartridge.cid in self._temp_dirs:
                temp_path = self._temp_dirs[cartridge.cid]
                if temp_path.exists():
                    shutil.rmtree(temp_path)
                del self._temp_dirs[cartridge.cid]
            return None

    def is_cartridge_available(self, cartridge_id: str) -> bool:
        """
        Check if a .playt file is available.

        Args:
            cartridge_id: Path to the .playt file

        Returns:
            True if the file exists and is a valid .playt file, False otherwise
        """
        playt_path = Path(cartridge_id)
        if not playt_path.exists():
            return False

        if playt_path.suffix.lower() != ".playt":
            return False

        try:
            # Verify it's a valid zip file
            with zipfile.ZipFile(playt_path, "r"):
                return True
        except (zipfile.BadZipFile, IOError):
            return False

    def _find_audio_files(self, directory: Path) -> list[Path]:
        """
        Find all audio files in the top-level directory (non-recursive).

        Only searches the top-level directory, not subdirectories.

        Args:
            directory: Directory to search

        Returns:
            List of audio file paths
        """
        audio_files: list[Path] = []

        if not directory.is_dir():
            return audio_files

        # Only search in the top-level directory, not subdirectories
        for item in directory.iterdir():
            if item.is_file() and item.suffix.lower() in self.AUDIO_EXTENSIONS:
                audio_files.append(item)

        return sorted(audio_files)

    def cleanup(self, cartridge_id: Optional[str] = None) -> None:
        """
        Clean up temporary directories.

        Args:
            cartridge_id: Specific cartridge to clean up, or None to clean all
        """
        if cartridge_id:
            if cartridge_id in self._temp_dirs:
                temp_dir = self._temp_dirs[cartridge_id]
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                del self._temp_dirs[cartridge_id]
            if cartridge_id in self._file_paths:
                del self._file_paths[cartridge_id]
        else:
            # Clean up all temp directories
            for temp_dir in self._temp_dirs.values():
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
            self._temp_dirs.clear()
            self._file_paths.clear()

    def __del__(self) -> None:
        """Cleanup on deletion."""
        self.cleanup()

