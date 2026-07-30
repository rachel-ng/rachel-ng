from __future__ import annotations

from pathlib import Path
from typing import Sequence
import json


def read_file(file_name: str | Path, lines: bool = True) -> str | list[str]:
    path = Path(file_name)
    if lines:
        return path.read_text(encoding="utf-8").splitlines(keepends=True)

    return path.read_text(encoding="utf-8")


def write_file(file_name: str | Path, content: str | Sequence[str], lines: bool = True) -> None:
    path = Path(file_name)
    if lines:
        path.write_text("".join(content), encoding="utf-8")
    else:
        path.write_text(content, encoding="utf-8")


def read_json(file_name: str | Path) -> dict:
    path = Path(file_name)
    return json.loads(path.read_text(encoding="utf-8"))
