from pathlib import Path

import pypdfium2 as pdfium

from app.utils import output_path


def split_pdf_by_ranges(input_path: Path, ranges: list[int]) -> Path:
    src = pdfium.PdfDocument(str(input_path))
    dest = pdfium.PdfDocument.new()

    for idx in ranges:
        dest.import_pages(src, pages=[idx - 1])

    out = output_path("_split.pdf")
    dest.save(str(out))
    dest.close()
    src.close()
    return out


def split_pdf_all_pages(input_path: Path) -> list[tuple[int, Path]]:
    src = pdfium.PdfDocument(str(input_path))
    results: list[tuple[int, Path]] = []

    for i in range(len(src)):
        dest = pdfium.PdfDocument.new()
        dest.import_pages(src, pages=[i])
        out = output_path(f"_page_{i + 1}.pdf")
        dest.save(str(out))
        dest.close()
        results.append((i + 1, out))

    src.close()
    return results
