from nicegui import ui

MENU_ITEMS = [
    {'label': 'Головна сторінка', 'icon': 'home', 'path': '/'},
    {'label': 'Додати зображення', 'icon': 'add_photo_alternate', 'path': '/image/create'},
    {'label': 'Гайд', 'icon': 'lightbulb', 'path': '/questions'},
    # {'label': 'ТЕСТ', 'icon': 'lightbulb', 'path': '/test'},
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