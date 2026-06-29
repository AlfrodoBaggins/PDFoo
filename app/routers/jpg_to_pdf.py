from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from app.utils import save_upload
from app.services.jpg_to_pdf import jpg_to_pdf
from app.download import store

router = APIRouter()


@router.post("/jpg-to-pdf")
async def jpg_to_pdf_endpoint(files: list[UploadFile] = File(...)):
    paths = []
    for f in files:
        data = await f.read()
        paths.append(save_upload(data, suffix=".jpg"))

    result = jpg_to_pdf(paths)

    for p in paths:
        p.unlink(missing_ok=True)

    token = store(result)
    return JSONResponse({"token": token, "name": "converted.pdf", "type": "application/pdf"})
