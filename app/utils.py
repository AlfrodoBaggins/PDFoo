import uuid
from pathlib import Path

from app.config import UPLOAD_DIR, OUTPUT_DIR


def save_upload(file_bytes: bytes, suffix: str = ".pdf") -> Path:
    name = f"{uuid.uuid4().hex}{suffix}"
    path = UPLOAD_DIR / name
    path.write_bytes(file_bytes)
    return path


def output_path(suffix: str = ".pdf") -> Path:
    name = f"{uuid.uuid4().hex}{suffix}"
    return OUTPUT_DIR / name


def parse_page_range(text: str, total: int) -> list[int]:
    pages: set[int] = set()
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            start = int(a.strip())
            end = int(b.strip()) if b.strip() else total
            pages.update(range(start, min(end, total) + 1))
        else:
            p = int(part)
            if 1 <= p <= total:
                pages.add(p)
    return sorted(pages)
