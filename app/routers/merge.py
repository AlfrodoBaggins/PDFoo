from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from app.utils import save_upload
from app.services.merger import merge_pdfs
from app.download import store

router = APIRouter()


@router.post("/merge")
async def merge_endpoint(files: list[UploadFile] = File(...)):
    paths = []
    for f in files:
        data = await f.read()
        paths.append(save_upload(data))

    result = merge_pdfs(paths)
    token = store(result)

    for p in paths:
        p.unlink(missing_ok=True)

    return JSONResponse({"token": token, "name": "merged.pdf", "type": "application/pdf"})
