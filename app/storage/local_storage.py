import os
from pathlib import Path
from app.storage.base import BaseStorage
from app.core.config import get_settings

settings = get_settings()


class LocalStorage(BaseStorage):
    def __init__(self, base_dir: str = settings.UPLOAD_DIR):
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_safe_path(self, path_or_key: str) -> Path:
        target = (self.base_dir / path_or_key).resolve()
        # Prevent directory traversal attacks
        if not str(target).startswith(str(self.base_dir)):
            raise ValueError(f"Directory traversal detected: {path_or_key}")
        return target

    async def save(self, file_data: bytes, filename: str, subfolder: str = "") -> str:
        folder = self.base_dir / subfolder
        folder.mkdir(parents=True, exist_ok=True)
        file_path = folder / filename
        with open(file_path, "wb") as f:
            f.write(file_data)
        # Return relative path for portability
        return str(file_path.relative_to(self.base_dir))

    async def read(self, path_or_key: str) -> bytes:
        target = self._resolve_safe_path(path_or_key)
        if not target.exists():
            raise FileNotFoundError(f"File not found: {path_or_key}")
        with open(target, "rb") as f:
            return f.read()

    async def delete(self, path_or_key: str) -> bool:
        target = self._resolve_safe_path(path_or_key)
        if target.exists():
            target.unlink()
            return True
        return False

    async def exists(self, path_or_key: str) -> bool:
        target = self._resolve_safe_path(path_or_key)
        return target.exists()

    def get_absolute_path(self, path_or_key: str) -> Path:
        return self._resolve_safe_path(path_or_key)
