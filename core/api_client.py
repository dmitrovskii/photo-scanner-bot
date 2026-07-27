import httpx 
from config import config

class EmbeddingApiClient:
    def __init__(self, base_url: str = config.embedding_service_url): 
        self.base_url = base_url 

    async def get_image_embedding(self, image_bytes: bytes) -> list[float]:
        files = {
            "file": ("photo.jpg", image_bytes, "image/jpeg")
        }

        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post("/v1/embeddings", files=files, timeout=10.0)
            response.raise_for_status()

            data = response.json()
            return data["vector"]
     