import logging
import shutil
import subprocess
from pathlib import Path

import pikepdf

from app.utils import output_path

logger = logging.getLogger("pdfoo")

GS_SETTINGS = {
    "maximum": "/screen",
    "recommended": "/ebook",
    "minimum": "/printer",
}

_HAS_GS: bool | None = None


def _check_ghostscript() -> bool:
    global _HAS_GS
    if _HAS_GS is None:
        _HAS_GS = shutil.which("gs") is not None
    return _HAS_GS


def compress_pdf(input_path: Path, level: str = "recommended") -> Path:
    if level not in GS_SETTINGS:
        level = "recommended"

    if _check_ghostscript():
        return _compress_with_gs(input_path, GS_SETTINGS[level])

    logger.warning("Ghostscript not found, falling back to lossless compression")
    return _compress_lossless(input_path)


def _compress_with_gs(input_path: Path, setting: str) -> Path:
    out = output_path("_compressed.pdf")
    subprocess.run(
        [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.7",
            f"-dPDFSETTINGS={setting}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-dSAFER",
            f"-sOutputFile={out}",
            str(input_path),
        ],
        check=True,
        capture_output=True,
    )
    return out


def _compress_lossless(input_path: Path) -> Path:
    out = output_path("_compressed.pdf")
    with pikepdf.open(input_path) as pdf:
        pdf.save(
            out,
            compress_streams=True,
            recompress_flate=True,
            stream_decode_level=pikepdf.StreamDecodeLevel.specialized,
        )
    return out
