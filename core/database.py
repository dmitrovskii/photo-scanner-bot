import uuid
from pathlib import Path
from datetime import datetime, timezone
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, PayloadSchemaType

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
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )

    await client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="category",
        field_schema=PayloadSchemaType.KEYWORD
    )

async def add_item(tg_file_id: str, vector: list, photo_path: str | Path, category: str = "default"):
    item_id = create_uuid(tg_file_id)

    payload = {
        "category": category,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "photo_path": photo_path      
    }

    await client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=item_id,
                vector=vector,
                payload=payload
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