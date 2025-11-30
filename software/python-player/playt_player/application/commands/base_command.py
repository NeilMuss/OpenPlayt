"""Base command interface following the Command pattern."""

from abc import ABC, abstractmethod


class Command(ABC):
    """
    Abstract command interface following the Command pattern.

    Commands encapsulate actions as objects, allowing for undo/redo,
    queuing, logging, and macro operations.
    """

    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass
