import os

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

from sentence_transformers import SentenceTransformer
from PIL import Image
from pathlib import Path

model = SentenceTransformer("clip-ViT-B-32", device="cpu")

def get_image_embedding(image_path: str | Path) -> list:
    result = Image.open(str(image_path))
    embeddings = model.encode(result)
    return embeddings.tolist()

