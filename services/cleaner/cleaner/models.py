from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FileResult:
    kind: str
    suspicious: bool
    report: dict[str, Any]
