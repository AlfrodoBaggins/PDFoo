import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.config import HOST, PORT, BASE_DIR
from app.download import consume
from app.routers import merge, split, compress, rotate, pdf_to_jpg, jpg_to_pdf

logger = logging.getLogger("pdfoo")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    for d in [BASE_DIR / "uploads", BASE_DIR / "outputs"]:
        if d.exists():
            for f in d.iterdir():
                if f.is_file():
                    f.unlink(missing_ok=True)


app = FastAPI(title="PDFoo", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(merge.router, prefix="/api")
app.include_router(split.router, prefix="/api")
app.include_router(compress.router, prefix="/api")
app.include_router(rotate.router, prefix="/api")
app.include_router(pdf_to_jpg.router, prefix="/api")
app.include_router(jpg_to_pdf.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/download/{token}")
async def download(token: str):
    path = consume(token)
    if path is None:
        raise HTTPException(404, "Download token not found or expired")
    suffix = path.suffix.lower()
    media_types = {
        ".pdf": "application/pdf",
        ".zip": "application/zip",
    }
    mime = media_types.get(suffix, "application/octet-stream")

    def stream():
        with open(path, "rb") as f:
            yield from f
        path.unlink(missing_ok=True)

    name = path.name
    return StreamingResponse(
        stream(),
        media_type=mime,
        headers={"Content-Disposition": f"attachment; filename={name}"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
