"""CLI logger implementation with observer pattern for output handling."""

from enum import Enum
from typing import Any, Optional, TextIO

from ...domain.interfaces.observer import Observer, Subject


class LogLevel(Enum):
    """Log levels for CLI output."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class CLIOutputObserver(Observer):
    """Observer that writes log messages to an output stream."""

    def __init__(self, output_stream: TextIO, error_stream: Optional[TextIO] = None) -> None:
        """
        Initialize the output observer.

        Args:
            output_stream: Stream for standard output (e.g., sys.stdout)
            error_stream: Stream for error output (e.g., sys.stderr). If None, uses output_stream
        """
        self._output_stream = output_stream
        self._error_stream = error_stream if error_stream is not None else output_stream

    def update(self, event_type: str, data: Any) -> None:
        """
        Receive a log message and write it to the appropriate stream.

        Args:
            event_type: Event type - "log_message" for log messages
            data: Dict with 'level', 'message', and optionally 'use_stderr'
        """
        if event_type == "log_message":
            level = data.get("level", LogLevel.INFO)
            message = data.get("message", "")
            use_stderr = data.get("use_stderr", False)

            stream = self._error_stream if use_stderr else self._output_stream
            stream.write(message)
            if not message.endswith("\n"):
                stream.write("\n")
            stream.flush()


class CLILogger(Subject):
    """
    Logger for CLI that supports observer pattern for output handling.

    This allows stdout/stderr to be observers that print log messages.
    """

    def __init__(self) -> None:
        """Initialize the CLI logger."""
        super().__init__()
        self._min_level = LogLevel.INFO

    def has_observers(self) -> bool:
        """
        Check if logger has any observers attached.

        Returns:
            True if observers are attached, False otherwise
        """
        return len(self._observers) > 0

    def set_level(self, level: LogLevel) -> None:
        """
        Set the minimum log level.

        Args:
            level: Minimum level to log
        """
        self._min_level = level

    def _log(self, level: LogLevel, message: str, use_stderr: bool = False) -> None:
        """
        Log a message at the specified level.

        Args:
            level: Log level
            message: Message to log
            use_stderr: Whether to use stderr stream
        """
        # Check if message should be logged based on level
        level_order = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR]
        if level_order.index(level) < level_order.index(self._min_level):
            return

        # Notify observers with log message
        self.notify("log_message", {"level": level, "message": message, "use_stderr": use_stderr})

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self._log(LogLevel.DEBUG, message)

    def info(self, message: str) -> None:
        """Log an info message."""
        self._log(LogLevel.INFO, message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self._log(LogLevel.WARNING, message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self._log(LogLevel.ERROR, message, use_stderr=True)


# Global CLI logger instance
_cli_logger: Optional[CLILogger] = None


def get_cli_logger() -> CLILogger:
    """
    Get the global CLI logger instance.

    Returns:
        Global CLILogger instance
    """
    global _cli_logger
    if _cli_logger is None:
        _cli_logger = CLILogger()
    return _cli_logger

