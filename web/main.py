from nicegui import ui

from core.database import get_items

MENU_ITEMS = [
    {'label': 'Головна сторінка', 'icon': 'home', 'path': '/'},
    {'label': 'Додати зображення', 'icon': 'add_photo_alternate', 'path': '/image/create'},
    {'label': 'Гайд', 'icon': 'lightbulb', 'path': '/questions'},
]

def setup_layout():
    with ui.header(elevated=True).classes('items-center justify-start'):
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
        ui.label("HEADER")

    with ui.left_drawer(fixed=False).classes('items-center p-2 space-y-1').props('bordered') as left_drawer:
        ui.label('Меню навігації').classes('text-xm font-bold text-gray-600')

        for item in MENU_ITEMS:
            ui.button(item['label'], icon=item['icon']) \
                .props('flat align=left color=grey-9') \
                .classes('w-full justify-start rounded-lg px-3') \
                .on('click', lambda _, p=item['path']: ui.navigate.to(p))

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
                    ui.image(item["photo_path"]) \
                        .classes('w-40 aspect-square cursor-pointer') \
                        .on('click', lambda img=item["photo_path"]: self.open_photo(img))

@ui.page('/questions')
async def questions_page():
    setup_layout()

@ui.page("/image/create")
async def create_page():
    setup_layout()

@ui.page("/")
async def control_page():
    setup_layout()

    gallery = GalleryComponent()
    await gallery.render() # type: ignore

ui.run()