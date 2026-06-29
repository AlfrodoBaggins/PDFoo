from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.utils import save_upload
from app.services.compressor import compress_pdf
from app.download import store

router = APIRouter()


@router.post("/compress")
async def compress_endpoint(
    file: UploadFile = File(...),
    level: str = Form("recommended"),
):
    data = await file.read()
    path = save_upload(data)

    result = compress_pdf(path, level=level)
    path.unlink(missing_ok=True)

    token = store(result)
    return JSONResponse({"token": token, "name": "compressed.pdf", "type": "application/pdf"})
