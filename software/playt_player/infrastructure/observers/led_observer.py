"""LED observer stub for future hardware integration."""

from typing import Any

from ...domain.interfaces.observer import Observer


class LEDObserver(Observer):
    """
    Observer stub for LED feedback on physical hardware.

    This is a placeholder for future hardware integration where
    LED patterns will reflect playback state.
    """

    def __init__(self) -> None:
        """Initialize the LED observer."""
        self._current_state = "idle"

    def update(self, event_type: str, data: Any) -> None:
        """
        Update LED state based on event.

        Args:
            event_type: Type of event
            data: Event data
        """
        # Stub implementation - will be replaced with actual hardware control
        if event_type == "track_started":
            self._current_state = "playing"
            # TODO: Set LED pattern for playing
        elif event_type == "track_paused":
            self._current_state = "paused"
            # TODO: Set LED pattern for paused
        elif event_type == "track_stopped":
            self._current_state = "stopped"
            # TODO: Set LED pattern for stopped
        elif event_type == "queue_ended":
            self._current_state = "idle"
            # TODO: Set LED pattern for idle

    def get_state(self) -> str:
        """
        Get the current LED state.

        Returns:
            Current state string
        """
        return self._current_state





