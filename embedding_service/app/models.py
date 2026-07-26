import os

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

import gc
import torch
import logging
from PIL import Image
from transformers import AutoImageProcessor, AutoModel
from embedding_service.config import config 

class EmbeddingService:
    def __init__(self, model_name=config.model_name):
        self.model_name = model_name
        self.processor = None
        self.model = None

    def load_model(self):
        self.processor = AutoImageProcessor.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)

    def get_image_embedding(self, image: Image.Image) -> list[float]:
        if self.processor is None or self.model is None:
            raise RuntimeError("Модель або процесор не ініціалізовані. Викличте метод завантаження.")
        
        try: 
            result = image.convert("RGB")
            inputs = self.processor(images=result, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model(**inputs)
                embedding = outputs.last_hidden_state[:, 0, :].squeeze().tolist()
            return embedding
        
        except Exception as e:
            logging.error(f"[ERROR] {e}")
            raise

    def unload_model(self):
        if self.processor is None or self.model is None:
            raise RuntimeError("Модель або процесор не ініціалізовані. Викличте метод завантаження.")
        self.processor = None
        self.model = None
        gc.collect()