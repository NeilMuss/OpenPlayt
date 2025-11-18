#!/usr/bin/env python3
"""Verification script to check that the project is set up correctly."""

import sys
from pathlib import Path

def check_imports() -> bool:
    """Check that all main modules can be imported."""
    try:
        from playt_player.domain.entities import Song, Album, Library
        from playt_player.domain.interfaces import AudioPlayerInterface, Observer, Subject
        from playt_player.application.commands import PlayCommand, PauseCommand
        from playt_player.application.player_service import PlayerService
        from playt_player.infrastructure.audio import FFmpegAudioPlayer
        from playt_player.infrastructure.cartridge import LocalFileCartridgeReader
        from playt_player.infrastructure.observers import LoggingObserver, LEDObserver
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def check_entities() -> bool:
    """Check that entities can be instantiated."""
    try:
        from playt_player.domain.entities import Song, Album
        
        song = Song(
            title="Test",
            artist="Artist",
            album="Album",
            duration_secs=100.0,
            file_path="/test.mp3"
        )
        album = Album(title="Album", artist="Artist", songs=[song])
        
        assert song.title == "Test"
        assert len(album.songs) == 1
        print("✓ Entities can be instantiated")
        return True
    except Exception as e:
        print(f"✗ Entity error: {e}")
        return False

def main() -> int:
    """Run all verification checks."""
    print("Verifying Playt Player setup...")
    print()
    
    checks = [
        ("Imports", check_imports),
        ("Entities", check_entities),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"Checking {name}...")
        if not check_func():
            all_passed = False
        print()
    
    if all_passed:
        print("✓ All checks passed! Setup is correct.")
        return 0
    else:
        print("✗ Some checks failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())






