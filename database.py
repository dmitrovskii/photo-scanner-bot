import uuid
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

#TODO: ПЕРЕНЕСТИ БАЗУ ДАНИХ НА АСИНХРОННІСТЬ + ДОККЕР

client = QdrantClient(path="qdrant_db")
COLLLECTION_NAME = "anime_merch"

def create_uuid(file_name: str) -> str:
    clear_file_name = Path(file_name).stem
    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, clear_file_name))
    return point_id

def init_db():
    if not client.collection_exists(COLLLECTION_NAME):
        client.create_collection(
            collection_name=COLLLECTION_NAME,
            vectors_config=VectorParams(size=512, distance=Distance.COSINE)
        )

def add_item(tg_file_id: str, vector: list, photo_path: str | Path, title: str = ""):
    item_id = create_uuid(tg_file_id)
    client.upsert(
        collection_name=COLLLECTION_NAME,
        points=[
            PointStruct(
                id=item_id,
                vector=vector,
                payload={
                    "title": title,
                    "photo_path": photo_path
                }
            )
        ]
    )

def search_items(vector_search: list, limit: int = 1):
    results = client.query_points(
        collection_name=COLLLECTION_NAME,
        query=vector_search,
        limit=limit
    )
    return results

def close_db():
    client.close()