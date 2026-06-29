import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

HOST = os.getenv("PDFOO_HOST", "127.0.0.1")
PORT = int(os.getenv("PDFOO_PORT", "8456"))
MAX_UPLOAD_SIZE = 200 * 1024 * 1024  # 200 MB
