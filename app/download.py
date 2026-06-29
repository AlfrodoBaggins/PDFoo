import uuid
from pathlib import Path

_pending: dict[str, Path] = {}


def store(path: Path) -> str:
    token = uuid.uuid4().hex
    _pending[token] = path
    return token


def consume(token: str) -> Path | None:
    return _pending.pop(token, None)
