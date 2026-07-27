from io import BytesIO
from PIL import Image
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from embedding_service.app.models import EmbeddingService

@asynccontextmanager
async def lifespan(app: FastAPI):
    service = EmbeddingService()
    service.load_model()
    app.state.embedding_service = service

    yield

    app.state.embedding_service.unload_model()

app = FastAPI(lifespan=lifespan)

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
async def generate_embedding(request: Request, file: UploadFile = File(...)):

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Переданий файл не є зображенням"
        )

    try:
        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes))
        service = request.app.state.embedding_service
        vector = service.get_image_embedding(image)

        return {"vector": vector}
    except Exception as e: 
        raise HTTPException(
            status_code=500,
            detail=f"Сталася помилка серверу {str(e)}"
        )
    