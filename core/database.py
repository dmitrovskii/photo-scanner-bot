from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    PayloadSchemaType,
    PointIdsList,
    PointStruct,
    VectorParams,
)

from config import config

client = AsyncQdrantClient(url=config.qdrant_url)
COLLECTION_NAME = config.collection_name

async def init_db() -> None:
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


async def add_items(
        item_ids: list[str],
        vectors: list[list[float]],
        photo_paths: list[str | Path],
        category: str = "default",
        descriptions: list[str] | None = None,
) -> None:
    if not (len(item_ids) == len(vectors) == len(photo_paths)):
        raise ValueError("Довжини списків IDs, векторів та шляхів мають збігатися")

    dtnow = datetime.now(timezone.utc).isoformat()

    points = [
        PointStruct(
            id=item_id,
            vector=vector,
            payload={
                "category": category,
                "created_at": dtnow,
                "photo_path": str(photo_path), 
                "description": desc
            },
        )
        for item_id, vector, photo_path, desc in zip(
            item_ids, vectors, photo_paths, descriptions
        )
    ]
    await client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )


async def add_item(
        item_id: str, 
        vector: list[float], 
        photo_path: str | Path, 
        category: str = "default",
        descriptions: str = ""
) -> None:
    await add_items(
        item_ids=[item_id],
        vectors=[vector],
        photo_paths=[photo_path],
        category=category,
        descriptions=[descriptions]
    )


async def search_items(vector: list[float], limit: int = 1) -> Any:
    results = await client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=limit
    )
    return results


async def delete_items(item_ids: list[str]) -> None:
    if not item_ids:
        return

    await client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=PointIdsList(points=points) # type: ignore
    )


async def get_items(
        limit: int = 20, offset: Any = None
        ) -> tuple[list[dict[str, Any]], Any]:
    records, next_offset = await client.scroll(
        collection_name=COLLECTION_NAME,
        limit=limit,
        offset=offset,
        with_payload=True,
        with_vectors=False
    )
    
    formatted_records = []
    for r in records:
        if r.payload is None:
            continue

        photo_path = r.payload.get("photo_path")
        if not photo_path:
            continue    

        formatted_records.append({
            "id": r.id,
            "photo_path": r.payload.get("photo_path"),
            "category": r.payload.get("category", "default"),
            "created_at": r.payload.get("created_at") 
        })

    return formatted_records, next_offset


async def close_db():
    await client.close()