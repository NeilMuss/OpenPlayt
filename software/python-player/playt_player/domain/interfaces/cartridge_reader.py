"""Cartridge reader interface for physical media integration."""

from abc import ABC, abstractmethod
from typing import Optional

from ..entities.album import Album
from ..entities.cartridge import Cartridge


class CartridgeReaderInterface(ABC):
    """
    Abstract interface for reading cartridge metadata and content.

    This interface allows different cartridge implementations (NFC, filesystem,
    network, etc.) to be swapped without changing the application layer.
    """

    @abstractmethod
    def read_cartridge(self, cartridge_id: str) -> Optional[Cartridge]:
        """
        Read cartridge metadata by ID.

        Args:
            cartridge_id: Unique identifier for the cartridge

        Returns:
            Cartridge object if found, None otherwise
        """
        pass

    @abstractmethod
    def load_album_from_cartridge(self, cartridge: Cartridge) -> Optional[Album]:
        """
        Load album data from a cartridge.

        Args:
            cartridge: The cartridge to read from

        Returns:
            Album object if successfully loaded, None otherwise
        """
        pass

    @abstractmethod
    def is_cartridge_available(self, cartridge_id: str) -> bool:
        """
        Check if a cartridge is available for reading.

        Args:
            cartridge_id: Unique identifier for the cartridge

        Returns:
            True if cartridge is available, False otherwise
        """
        pass


