"""Command-line interface for the audio player."""

import sys
from pathlib import Path
from typing import Optional

from ...application.commands.next_command import NextCommand
from ...application.commands.pause_command import PauseCommand
from ...application.commands.play_command import PlayCommand
from ...application.commands.prev_command import PrevCommand
from ...application.commands.stop_command import StopCommand
from ...application.player_service import PlayerService
from ...domain.interfaces.audio_player import AudioPlayerInterface
from ...domain.interfaces.cartridge_reader import CartridgeReaderInterface
from ...infrastructure.audio.ffmpeg_audio_player import FFmpegAudioPlayer
from ...infrastructure.cartridge.playt_file_cartridge_reader import PlaytFileCartridgeReader
from ...infrastructure.observers.logging_observer import LoggingObserver


class PlayerCLI:
    """Command-line interface for interacting with the player."""

    def __init__(
        self,
        player_service: PlayerService,
        cartridge_reader: Optional[CartridgeReaderInterface] = None,
    ) -> None:
        """
        Initialize the CLI.

        Args:
            player_service: The player service to control
            cartridge_reader: Optional cartridge reader for loading albums
        """
        self._player_service = player_service
        self._cartridge_reader = cartridge_reader
        self._setup_observers()

    def _setup_observers(self) -> None:
        """Set up default observers."""
        logging_observer = LoggingObserver()
        self._player_service.attach(logging_observer)

    def run_interactive(self, auto_play: bool = False) -> None:
        """
        Run the interactive CLI loop.

        Args:
            auto_play: If True, automatically start playing after loading an album
        """
        print("Playt Player - Interactive Mode")
        print("Commands: play, pause, stop, next, prev, load <cartridge_id|file_path>, quit")
        print()

        while True:
            try:
                command = input("> ").strip().lower()

                if command == "quit" or command == "q":
                    break
                elif command == "play":
                    PlayCommand(self._player_service).execute()
                elif command == "pause":
                    PauseCommand(self._player_service).execute()
                elif command == "stop":
                    StopCommand(self._player_service).execute()
                elif command == "next":
                    NextCommand(self._player_service).execute()
                elif command == "prev":
                    PrevCommand(self._player_service).execute()
                elif command.startswith("load "):
                    cartridge_id = command[5:].strip()
                    self._load_cartridge(cartridge_id)
                elif command == "status":
                    self._show_status()
                elif command == "help":
                    self._show_help()
                else:
                    print(f"Unknown command: {command}. Type 'help' for commands.")
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

    def _load_cartridge(self, cartridge_id: str) -> None:
        """Load an album from a cartridge or .playt file."""
        # Check if it looks like a .playt file path (by extension)
        cartridge_path = Path(cartridge_id)
        is_playt_file_by_extension = cartridge_path.suffix.lower() == ".playt"

        # If it looks like a .playt file and we don't have a reader, create one
        # We'll let the reader itself check if the file actually exists
        if is_playt_file_by_extension and not self._cartridge_reader:
            from ...infrastructure.cartridge.playt_file_cartridge_reader import (
                PlaytFileCartridgeReader,
            )

            self._cartridge_reader = PlaytFileCartridgeReader()

            # Try to resolve the path - handle both absolute and relative paths
            if not cartridge_path.is_absolute():
                # Try resolving relative to current working directory
                resolved_path = Path.cwd() / cartridge_path
                if resolved_path.exists():
                    cartridge_id = str(resolved_path.absolute())

        if not self._cartridge_reader:
            print("Cartridge reader not available")
            return

        if not self._cartridge_reader.is_cartridge_available(cartridge_id):
            print(f"Cartridge not found: {cartridge_id}")
            return

        cartridge = self._cartridge_reader.read_cartridge(cartridge_id)
        if not cartridge:
            print(f"Failed to read cartridge: {cartridge_id}")
            return

        album = self._cartridge_reader.load_album_from_cartridge(cartridge)
        if not album:
            print(f"Failed to load album from cartridge: {cartridge_id}")
            return

        self._player_service.load_album(album)
        print(f"Loaded album: {album.title} by {album.artist}")
        print(f"  {len(album.songs)} songs loaded")
        for idx, song in enumerate(album.ordered_songs(), start=1):
            print(f"  {idx}. {song.title}")

    def _show_status(self) -> None:
        """Show current player status."""
        song = self._player_service.get_current_song()
        state = self._player_service.get_state()
        position = self._player_service.get_position()

        if song:
            pos_str = f"{position:.1f}s" if position else "?"
            print(f"State: {state}, Song: {song.title}, Position: {pos_str}")
        else:
            print(f"State: {state}, No song loaded")

    def _show_help(self) -> None:
        """Show help message."""
        print("Available commands:")
        print("  play          - Start or resume playback")
        print("  pause         - Pause playback")
        print("  stop          - Stop playback")
        print("  next          - Skip to next track")
        print("  prev          - Go to previous track")
        print("  load <path>   - Load album from cartridge or .playt file")
        print("  status        - Show current status")
        print("  help          - Show this help")
        print("  quit / q      - Exit the player")


def create_player_service(audio_player: Optional[AudioPlayerInterface] = None) -> PlayerService:
    """
    Factory function to create a player service with default dependencies.

    Args:
        audio_player: Optional audio player (defaults to LocalFileAudioPlayer)

    Returns:
        Configured PlayerService instance
    """
    if audio_player is None:
        audio_player = FFmpegAudioPlayer()
    return PlayerService(audio_player)


def main() -> None:
    """Main entry point for the CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Playt Player - Audio player for .playt cartridge files"
    )
    parser.add_argument(
        "playt_file",
        nargs="?",
        help="Path to a .playt file to load and play",
    )
    parser.add_argument(
        "--auto-play",
        action="store_true",
        help="Automatically start playing after loading the album",
    )

    args = parser.parse_args()

    try:
        player_service = create_player_service()

        # If a .playt file is provided, use PlaytFileCartridgeReader
        cartridge_reader: Optional[CartridgeReaderInterface] = None
        if args.playt_file:
            playt_path = Path(args.playt_file)
            if not playt_path.exists():
                print(f"Error: File not found: {args.playt_file}", file=sys.stderr)
                sys.exit(1)

            if playt_path.suffix.lower() != ".playt":
                print(
                    f"Error: File does not have .playt extension: {args.playt_file}",
                    file=sys.stderr,
                )
                sys.exit(1)

            cartridge_reader = PlaytFileCartridgeReader()

        cli = PlayerCLI(player_service, cartridge_reader)

        # If a .playt file was provided, load it automatically
        if args.playt_file and cartridge_reader:
            print(f"Loading .playt file: {args.playt_file}")
            cli._load_cartridge(str(playt_path.absolute()))
            if args.auto_play:
                print("Starting playback...")
                PlayCommand(player_service).execute()

        cli.run_interactive(auto_play=args.auto_play)
    except Exception as e:
        print(f"Failed to start player: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()






