"""Playt file cartridge reader implementation for .playt zip files."""

import shutil
import tempfile
import zipfile
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
                        break

            if not audio_files:
                # Clean up temp directory if no audio files found
                shutil.rmtree(temp_dir)
                return None

            # Create songs from audio files
            songs: list[Song] = []
            for idx, audio_file in enumerate(sorted(audio_files), start=1):
                # Get filename without extension for title
                title = audio_file.stem

                # Create song - file_path will be absolute path to extracted file
                song = Song(
                    title=title,
                    artist="Unknown Artist",
                    album=cartridge.cid,  # Use cartridge ID as album name
                    duration_secs=None,  # Duration can be extracted later if needed
                    file_path=str(audio_file),
                    track_number=idx,
                    metadata={},
                )
                songs.append(song)

            # Create album
            album = Album(
                title=cartridge.cid,
                artist="Unknown Artist",
                year=None,
                genre=None,
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

