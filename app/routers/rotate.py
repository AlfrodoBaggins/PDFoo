from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import pypdfium2 as pdfium

from app.utils import save_upload, parse_page_range
from app.services.rotator import rotate_pdf
from app.download import store

router = APIRouter()


@router.post("/rotate")
async def rotate_endpoint(
    file: UploadFile = File(...),
    angle: int = Form(90),
    ranges: str = Form(""),
):
    if angle not in (90, 180, 270):
        raise HTTPException(400, "angle must be 90, 180, or 270")

    data = await file.read()
    path = save_upload(data)

    src = pdfium.PdfDocument(str(path))
    total = len(src)
    src.close()

    if ranges.strip():
        page_indices = [i - 1 for i in parse_page_range(ranges, total)]
    else:
        page_indices = None

    result = rotate_pdf(path, angle, page_indices)
    path.unlink(missing_ok=True)

    token = store(result)
    return JSONResponse({"token": token, "name": "rotated.pdf", "type": "application/pdf"})
