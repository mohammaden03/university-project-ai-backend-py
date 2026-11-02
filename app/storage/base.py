from abc import ABC, abstractmethod
from typing import BinaryIO, Optional


class BaseStorage(ABC):
    @abstractmethod
    async def save(self, file_data: bytes, filename: str, subfolder: str = "") -> str:
        """Saves file data and returns its stored path or key."""
        pass

    @abstractmethod
    async def read(self, path_or_key: str) -> bytes:
        """Reads file data as bytes."""
        pass

    @abstractmethod
    async def delete(self, path_or_key: str) -> bool:
        """Deletes file."""
        pass

    @abstractmethod
    async def exists(self, path_or_key: str) -> bool:
        """Checks if file exists."""
        pass
