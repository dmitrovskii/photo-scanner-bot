from nicegui import ui
from core.database import get_items
from core.storage import get_photo_path

class GalleryComponent:
    def __init__(self) -> None:
        with ui.dialog() as self.dialog, ui.card().classes('w-full max-w-1xl p-2'):
            self.dialog_img = ui.image().classes('w-full')

        self.last_file_count = 0 
        
        ui.timer(interval=5.0, callback=self.check_new_photos)

    async def check_new_photos(self):
        items = await get_items()

        if len(items[0]) != self.last_file_count:
            self.last_file_count = len(items[0])
            self.render.refresh()

    def open_photo(self, img_path):
        self.dialog_img.set_source(img_path)
        self.dialog.open()

    @ui.refreshable
    async def render(self):
        with ui.row().classes('gap-1'):
            items, next_offset = await get_items()
            for item in items:
                with ui.card().tight().classes('no-shadow'):
                    image = get_photo_path(item["photo_path"])
                    ui.image(image) \
                        .classes('w-40 aspect-square cursor-pointer') \
                        .on('click', lambda img=image: self.open_photo(img))
