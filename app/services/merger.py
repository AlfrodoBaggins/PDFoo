from pathlib import Path

import pypdfium2 as pdfium

from app.utils import output_path


def merge_pdfs(input_paths: list[Path]) -> Path:
    out = output_path("_merged.pdf")
    dest = pdfium.PdfDocument.new()

    for path in input_paths:
        src = pdfium.PdfDocument(str(path))
        for i in range(len(src)):
            dest.import_pages(src, pages=[i])
        src.close()

    dest.save(str(out))
    dest.close()
    return out
