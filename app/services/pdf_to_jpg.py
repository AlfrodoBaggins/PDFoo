from pathlib import Path

import pypdfium2 as pdfium

from app.utils import output_path


def pdf_to_jpg(input_path: Path, dpi: int = 200) -> list[tuple[int, Path]]:
    src = pdfium.PdfDocument(str(input_path))
    results: list[tuple[int, Path]] = []

    for i in range(len(src)):
        page = src[i]
        bitmap = page.render(scale=dpi / 72)
        pil_image = bitmap.to_pil()
        out = output_path(f"_page_{i + 1}.jpg")
        pil_image.save(str(out), quality=92)
        results.append((i + 1, out))

    src.close()
    return results
