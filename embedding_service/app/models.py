import os

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

import gc
import torch
import psutil
import logging
from PIL import Image
from transformers import AutoImageProcessor, AutoModel
from embedding_service.config import config 

class EmbeddingService:
    def __init__(self, model_name=config.model_name):
        self.model_name = model_name
        self.processor = None
        self.model = None
        self.batch_size = psutil.cpu_count(logical=False) or 1

    def load_model(self):
        self.processor = AutoImageProcessor.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)

    def get_image_embedding(self, images: list[Image.Image]) -> list[list[float]]:
        if self.processor is None or self.model is None:
            raise RuntimeError("Модель або процесор не ініціалізовані. Викличте метод завантаження.")
        
        try:
            all_embeddings = []
            for i in range(0, len(images), self.batch_size):
                batch_images = images[i : i + self.batch_size]
                batch_rgb = [img.convert("RGB") for img in batch_images]
                inputs = self.processor(images=batch_rgb, return_tensors="pt")

                with torch.no_grad():
                    outputs = self.model(**inputs)
                    embeddings = outputs.last_hidden_state[:, 0, :].tolist()
                    all_embeddings.extend(embeddings)
            return all_embeddings
        
        except Exception as e:
            logging.error(f"[ERROR] {e}")
            raise

    def unload_model(self):
        if self.processor is None or self.model is None:
            raise RuntimeError("Модель або процесор не ініціалізовані. Викличте метод завантаження.")
        self.processor = None
        self.model = None
        gc.collect()