"""Previous track command implementation."""

from .base_command import Command


class PrevCommand(Command):
    """Command to go to the previous track."""

    def __init__(self, player_service: "PlayerService") -> None:
        """
        Initialize the previous command.

        Args:
            player_service: The player service to execute the command on
        """
        self._player_service = player_service

    def execute(self) -> None:
        """Execute the previous command."""
        self._player_service.previous()


# Forward reference type hint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..player_service import PlayerService





