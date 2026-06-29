import zipfile
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.utils import save_upload, output_path
from app.services.pdf_to_jpg import pdf_to_jpg
from app.download import store

router = APIRouter()


@router.post("/pdf-to-jpg")
async def pdf_to_jpg_endpoint(
    file: UploadFile = File(...),
    dpi: int = Form(200),
):
    data = await file.read()
    path = save_upload(data)

    pages = pdf_to_jpg(path, dpi=dpi)

    zip_out = output_path(".zip")
    with zipfile.ZipFile(str(zip_out), "w") as zf:
        for num, img_path in pages:
            zf.write(str(img_path), f"page_{num}.jpg")
            img_path.unlink(missing_ok=True)
    path.unlink(missing_ok=True)

    token = store(zip_out)
    return JSONResponse({"token": token, "name": "pages.zip", "type": "application/zip"})
