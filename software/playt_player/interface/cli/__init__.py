"""Command-line interface implementation."""

from importlib import import_module
from typing import Any

__all__ = ["PlayerCLI", "create_player_service", "main"]


def __getattr__(name: str) -> Any:
    if name in __all__:
        module = import_module(".player_cli", __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)






