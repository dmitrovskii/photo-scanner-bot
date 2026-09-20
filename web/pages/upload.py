import io
import base64

from PIL import Image
from nicegui import ui

from core.database import add_items
from core.storage import save_photo_bytes
from core.api_client import EmbeddingApiClient

class UploadPage:
    def __init__(self) -> None:
        self.uploaded_photos = []
        self.api_cleint = EmbeddingApiClient()
        self.MAX_MB = 100
        self.MAX_BYTES = self.MAX_MB * 1024 * 1024

    @ui.refreshable
    def render_photo_cards(self):
        if not self.uploaded_photos:
            ui.label("📸 Завантажте фото до форми вище").classes("text-gray-400 italic mt-4")
            return

        ui.label(f"{len(self.uploaded_photos)} фото завантажено")
        with ui.column().classes("w-full gap-4"):
            for idx, item in enumerate(self.uploaded_photos):
                with ui.card().classes("w-full p-3 border min-w-0"):
                    with ui.row().classes("items-center gap-4 w-full no-wrap"):
                        ui.image(item['b64_src']).classes("w-20 h-20 object-cover rounded-lg flex-shrink-0")

                        with ui.column().classes("flex-grow min-w-0"):
                            ui.label(item['name']).classes("font-bold text-sm text-gray-700 truncate w-full")
                            
                            ui.input(
                                placeholder="Додайте назву або опис...",
                                value=item['description'],
                                on_change=lambda e, i=idx: self.uploaded_photos[i].update({'description': e.value}) 
                            ).classes("w-full").props("dense clearable")

                        ui.button(
                            icon="delete", 
                            on_click=lambda e, i=idx: self.delete_photo(i)
                        ).props("flat round color=negative")

    async def handle_upload(self, e):
        file_size = e.file.size()
        if file_size > self.MAX_BYTES:
            ui.notify(f"Файл {e.file.name} перевищує ліміт у 100 МБ", type="negative")
            return

        file_bytes = await e.file.read()
        thumb_b64 = self.make_thumbnail_b64(file_bytes)    

        self.uploaded_photos.append({
            'name': e.file.name,
            'bytes': file_bytes,
            'b64_src': thumb_b64,
            'description': ''
        })

        self.render_photo_cards.refresh()

    def make_thumbnail_b64(self, file_bytes: bytes, size: tuple[int, int] = (120, 120)) -> str:
        with Image.open(io.BytesIO(file_bytes)) as img: 
            img.thumbnail(size)
            buffer = io.BytesIO()
            img.convert("RGB").save(buffer, format="JPEG", quality=70)
            encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded}" 

    async def submit_all(self):
        if not self.uploaded_photos:
            ui.notify("Спочатку завантажте хоча б одне фото!", type="warning")
            return

        try:
            images_bytes = [photo["bytes"] for photo in self.uploaded_photos]
            vectors = await self.api_cleint.get_embeddings(images_bytes)

            item_ids = []
            photo_paths = []
            descriptions = []

            for photo in self.uploaded_photos:
                item_id, file_name = save_photo_bytes(photo["bytes"])
                item_ids.append(item_id)
                photo_paths.append(file_name)
                descriptions.append(photo.get("description", ""))
                
            await add_items(
                item_ids=item_ids,
                vectors=vectors,
                photo_paths=photo_paths,
                descriptions=descriptions
            )

            ui.notify(f"Успішно оброблено {len(self.uploaded_photos)} фото!", type="positive")

            self.cancell_all()  

        except Exception as e:
            ui.notify(f"Помилка збереження: {e}", type="negative")
            
    def cancell_all(self):
        self.uploaded_photos.clear()
        self.render_photo_cards.refresh()

    def delete_photo(self, index: int):
        self.uploaded_photos.pop(index)
        self.render_photo_cards.refresh()

    def render(self):        
        with ui.column().classes("w-full gap-6 items-start no-wrap"):

            with ui.column().classes("w-1/3 min-w-[280px]"):
                ui.upload(
                    label="Перетягніть сюди фото",
                    multiple=True,              
                    auto_upload=True,       
                    on_upload=self.handle_upload,
                    max_file_size=self.MAX_BYTES,
                    max_total_size=self.MAX_BYTES,
                    on_rejected= lambda: ui.notify(f"Файл занадто великий! Максимум {self.MAX_MB} МБ", type="negative")

                ).classes("w-full").props('accept=image/*')
    
                ui.button("Зберегти в галерею", on_click=self.submit_all) \
                    .classes("w-full mt-4 bg-green-600 text-white font-bold")
                ui.button("Відмінити", on_click=self.cancell_all) \
                    .classes("w-full mt-4 bg-green-600 text-white font-bold")

            with ui.column().classes("w-full flex-grow"):
                ui.label("Завантажені файли:").classes("text-lg font-semibold")
                self.render_photo_cards() #type: ignore 