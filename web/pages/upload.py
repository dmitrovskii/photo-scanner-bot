import base64
from nicegui import ui

class UploadPage:
    def __init__(self) -> None:
        self.uploaded_photos = []

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
                                placeholder="Додайте опис або теги...",
                                value=item['description'],
                                on_change=lambda e, i=idx: self.uploaded_photos[i].update({'description': e.value})
                            ).classes("w-full").props("dense clearable")
                        ui.button(icon="delete", on_click=lambda e, i=idx: self.delete_photo(i)).props("flat round color=negative")

    async def handle_upload(self, e):
        file_bytes = await e.file.read()

        b64_encoded = base64.b64encode(file_bytes).decode('utf-8')
        b64_src = f"data:{e.file.content_type};base64,{b64_encoded}"

        self.uploaded_photos.append({
            'name': e.file.name,
            'bytes': file_bytes,
            'b64_src': b64_src,
            'description': ''
        })

        self.render_photo_cards.refresh()

    def submit_all(self):
        if not self.uploaded_photos:
            ui.notify("Спочатку завантажте хоча б одне фото!", type="warning")
            return

        # Відправка bytes у FastAPI (DINOv2)
        # Запис у Qdrant

        ui.notify(f"Успішно оброблено {len(self.uploaded_photos)} фото!", type="positive")

        for photo in self.uploaded_photos:
            print(f"Файл: {photo['name']} | Опис: {photo['description']} | Розмір: {len(photo['bytes'])} bytes")

        self.cancell_all()

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
                    max_files=8,            
                    auto_upload=True,       
                    on_upload=self.handle_upload
                ).classes("w-full").props('accept=image/*')
    
                ui.button("Зберегти в галерею", on_click=self.submit_all) \
                    .classes("w-full mt-4 bg-green-600 text-white font-bold")
                ui.button("Відмінити", on_click=self.cancell_all) \
                    .classes("w-full mt-4 bg-green-600 text-white font-bold")

            with ui.column().classes("w-full flex-grow"):
                ui.label("Завантажені файли:").classes("text-lg font-semibold")
                self.render_photo_cards() #type: ignore 

