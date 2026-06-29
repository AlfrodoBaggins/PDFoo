from pathlib import Path

import img2pdf

from app.utils import output_path


def jpg_to_pdf(input_paths: list[Path]) -> Path:
    out = output_path(".pdf")
    with open(str(out), "wb") as f:
        f.write(img2pdf.convert([str(p) for p in input_paths]))
    return out
