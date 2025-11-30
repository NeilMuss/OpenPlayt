"""Pause command implementation."""

from .base_command import Command


class PauseCommand(Command):
    """Command to pause playback."""

    def __init__(self, player_service: "PlayerService") -> None:
        """
        Initialize the pause command.

        Args:
            player_service: The player service to execute the command on
        """
        self._player_service = player_service

    def execute(self) -> None:
        """Execute the pause command."""
        self._player_service.pause()


# Forward reference type hint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..player_service import PlayerService
