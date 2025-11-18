"""Next track command implementation."""

from .base_command import Command


class NextCommand(Command):
    """Command to skip to the next track."""

    def __init__(self, player_service: "PlayerService") -> None:
        """
        Initialize the next command.

        Args:
            player_service: The player service to execute the command on
        """
        self._player_service = player_service

    def execute(self) -> None:
        """Execute the next command."""
        self._player_service.next()


# Forward reference type hint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..player_service import PlayerService






