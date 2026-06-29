from pathlib import Path

import pypdfium2 as pdfium

from app.utils import output_path


def rotate_pdf(input_path: Path, angle: int, page_indices: list[int] | None = None) -> Path:
    src = pdfium.PdfDocument(str(input_path))

    target = page_indices if page_indices is not None else list(range(len(src)))

    for i in target:
        page = src[i]
        cur = page.get_rotation()
        page.set_rotation((cur + angle) % 360)

    out = output_path("_rotated.pdf")
    src.save(str(out))
    src.close()
    return out
