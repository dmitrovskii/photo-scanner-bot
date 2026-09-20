import asyncio
from contextlib import asynccontextmanager
from io import BytesIO

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from PIL import Image
from starlette.concurrency import run_in_threadpool

from embedding_service.app.models import EmbeddingService

@asynccontextmanager
async def lifespan(app: FastAPI):
    service = EmbeddingService()
    service.load_model()
    app.state.embedding_service = service

    yield

    app.state.embedding_service.unload_model()

app = FastAPI(lifespan=lifespan)
semaphore = asyncio.Semaphore()

@app.get("/health")
async def health(request: Request):
    service = getattr(request.app.state, "embedding_service", None)

    is_ready = service is not None and service.model is not None
    return {
        "status": "ok" if is_ready else "unhealthy", 
        "model_loaded": is_ready, 
        "model_name": service.model_name if service else None
    }


@app.post("/v1/embeddings")
async def generate_embedding(request: Request, files: list[UploadFile] = File(...)):

    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="Переданий файл не є зображенням"
            )

    try:
        images = [Image.open(BytesIO(await f.read())) for f in files]
        async with semaphore:
            embeddings = await run_in_threadpool(
                request.app.state.embedding_service.get_image_embedding,
                images
            )
        return {"embeddings": embeddings}

    except Exception as e: 
        raise HTTPException(
            status_code=500,
            detail=f"Сталася помилка серверу {str(e)}"
        )
    