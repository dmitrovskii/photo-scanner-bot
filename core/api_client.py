import httpx 

class EmbeddingApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"): 
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
     