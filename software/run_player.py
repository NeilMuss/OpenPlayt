"""
This script provides a simple entry point for running the Playt Player CLI.

It handles the necessary sys.path manipulation to ensure that the
`playt_player` package and its dependencies can be found, regardless of
how the script is run.
"""

import os
import sys

# Add the 'python-player' directory to the Python path
# This allows the 'playt_player' package to be imported
script_dir = os.path.dirname(os.path.abspath(__file__))
python_player_dir = os.path.join(script_dir, "python-player")
sys.path.insert(0, python_player_dir)

from playt_player.interface.cli.player_cli import main

def run_gui_if_configured():
    """Check for custom UI and launch it if found."""
    # Check for ./ui-theme/custom-ui/index.html relative to CWD
    cwd = os.getcwd()
    custom_ui_path = os.path.join(cwd, "ui-theme", "custom-ui", "index.html")
    
    if os.path.exists(custom_ui_path):
        print(f"Found custom UI at {custom_ui_path}")
        try:
            import webview
            from playt_player.interface.gui.webview_ui import WebViewUI
            from playt_player.infrastructure.audio.visualization_stub import VisualizationStub
            from playt_player.interface.cli.player_cli import create_player_service
            from playt_player.infrastructure.cartridge.playt_file_cartridge_reader import PlaytFileCartridgeReader
            from playt_player.application.commands.play_command import PlayCommand
            from pathlib import Path
            import argparse

            # Parse arguments manually or use argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("playt_file", nargs="?", help="Path to .playt file")
            parser.add_argument("--auto-play", action="store_true")
            args, _ = parser.parse_known_args()
            
            service = create_player_service()
            stub = VisualizationStub()
            
            # Load cartridge if provided
            cartridge_reader_ref = None  # Keep reference to prevent cleanup
            if args.playt_file:
                playt_path = Path(args.playt_file)
                if playt_path.exists() and playt_path.suffix.lower() == ".playt":
                    reader = PlaytFileCartridgeReader()
                    cartridge_reader_ref = reader  # Prevent GC
                    
                    print(f"Loading cartridge: {playt_path}")
                    cartridge = reader.read_cartridge(str(playt_path.absolute()))
                    if cartridge:
                        album = reader.load_album_from_cartridge(cartridge)
                        if album:
                            service.load_album(album)
                            if args.auto_play:
                                service.play()
            
            ui = WebViewUI(service, custom_ui_path, stub)
            # Pass reader to UI if needed, or attach to ensure it lives as long as UI
            if cartridge_reader_ref:
                ui._cartridge_reader = cartridge_reader_ref
                
            ui.run()
            return True
        except ImportError as e:
            print(f"Could not launch GUI: {e}")
            print("Ensure pywebview is installed: python -m pip install pywebview")
            # Fall back to CLI
            return False
    return False

if __name__ == "__main__":
    if not run_gui_if_configured():
        main()
