from nicegui import ui
from web.pages.gallery import GalleryComponent
from web.pages.upload import UploadPage
from web.components.header import setup_layout

@ui.page('/questions')
async def questions_page():
    setup_layout()

@ui.page("/image/create")
async def create_page():
    setup_layout()

    upload = UploadPage()
    upload.render()

@ui.page("/")
async def control_page():
    setup_layout()

    gallery = GalleryComponent()
    await gallery.render() # type: ignore

ui.run(host="0.0.0.0", port=8080, title="Photo Scanner")