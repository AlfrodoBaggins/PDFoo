import zipfile
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import pypdfium2 as pdfium

from app.utils import save_upload, parse_page_range, output_path
from app.services.splitter import split_pdf_by_ranges, split_pdf_all_pages
from app.download import store

router = APIRouter()


@router.post("/split")
async def split_endpoint(
    file: UploadFile = File(...),
    ranges: str = Form(""),
):
    data = await file.read()
    path = save_upload(data)

    src = pdfium.PdfDocument(str(path))
    total = len(src)
    src.close()

    if ranges.strip():
        parsed = parse_page_range(ranges, total)
        result = split_pdf_by_ranges(path, parsed)
        path.unlink(missing_ok=True)
        token = store(result)
        return JSONResponse({"token": token, "name": "split.pdf", "type": "application/pdf"})

    pages = split_pdf_all_pages(path)
    zip_out = output_path(".zip")
    with zipfile.ZipFile(str(zip_out), "w") as zf:
        for num, p in pages:
            zf.write(str(p), f"page_{num}.pdf")
            p.unlink(missing_ok=True)
    path.unlink(missing_ok=True)
    token = store(zip_out)
    return JSONResponse({"token": token, "name": "pages.zip", "type": "application/zip"})
