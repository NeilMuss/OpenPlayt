from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Cartridge:
    cid: str                   # content hash or NFC chip ID
    security_level: str        # "open" or "locked"
    version: Optional[str] = None
