import httpx 
import asyncio
from config import config

class EmbeddingApiClient:
    def __init__(self, base_url: str = config.embedding_service_url, max_concurrent_requests: int = 1): 
        self.base_url = base_url
        self.semaphore = asyncio.Semaphore(max_concurrent_requests) 

    async def get_image_embedding(self, image_bytes: bytes) -> list[float]:
        embeddings = await self.get_embeddings([image_bytes])
        return embeddings[0]

    async def get_embeddings(self, images_bytes: list[bytes]) -> list[list[float]]:
        files = [
            ("files", (f"photo_{i}.jpg", img_bytes, "image/jpeg"))
            for i, img_bytes in enumerate(images_bytes)
        ]

        async with self.semaphore:
            async with httpx.AsyncClient(base_url=self.base_url) as client:
                response = await client.post("/v1/embeddings", files=files, timeout=60.0)
                response.raise_for_status()

                data = response.json()
                return data["embeddings"]