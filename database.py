import uuid
from pathlib import Path
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from config import config

client = AsyncQdrantClient(url=config.qdrant_url)
COLLECTION_NAME = "photo"

def create_uuid(file_name: str) -> str:
    clear_file_name = Path(file_name).stem
    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, clear_file_name))
    return point_id

async def init_db():
    if not await client.collection_exists(COLLECTION_NAME):
        await client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=512, distance=Distance.COSINE),
        )

async def add_item(tg_file_id: str, vector: list, photo_path: str | Path):
    item_id = create_uuid(tg_file_id)
    await client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=item_id,
                vector=vector,
                payload={
                    "photo_path": photo_path
                }
            )
        ]
    )

async def search_items(vector: list, limit: int = 1):
    results = await client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=limit
    )
    return results

async def close_db():
    await client.close()