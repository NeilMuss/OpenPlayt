"""Domain interfaces defining contracts for implementations."""

from .audio_player import AudioPlayerInterface
from .cartridge_reader import CartridgeReaderInterface
from .observer import Observer, Subject

__all__ = ["AudioPlayerInterface", "CartridgeReaderInterface", "Observer", "Subject"]





