from __future__ import annotations

from pathlib import Path
from typing import Literal

FileKind = Literal["text", "image", "container", "unsupported"]

_TEXT_EXTENSIONS = {".txt", ".md", ".markdown"}
_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
_CONTAINER_EXTENSIONS = {".pdf", ".docx"}


def _looks_binary(data: bytes) -> bool:
    if not data:
        return False
    sample = data[:8192]
    if b"\x00" in sample:
        return True
    controls = sum(1 for byte in sample if byte < 32 and byte not in (9, 10, 13, 12))
    return controls / max(len(sample), 1) > 0.05


def classify_bytes(data: bytes, filename: str) -> FileKind:
    suffix = Path(filename).suffix.lower()

    if data.startswith(b"\x89PNG\r\n\x1a\n") or data.startswith(b"\xff\xd8\xff"):
        return "image"
    if len(data) >= 12 and data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image"
    if data.startswith(b"%PDF-"):
        return "container"
    if data.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")):
        return "container" if suffix == ".docx" else "unsupported"

    if suffix in _IMAGE_EXTENSIONS or suffix in _CONTAINER_EXTENSIONS:
        return "unsupported"
    if suffix in _TEXT_EXTENSIONS and not _looks_binary(data):
        return "text"
    if not _looks_binary(data):
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            return "unsupported"
        return "text" if suffix in _TEXT_EXTENSIONS else "unsupported"
    return "unsupported"
