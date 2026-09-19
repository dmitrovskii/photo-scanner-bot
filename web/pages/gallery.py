from nicegui import ui
from core.database import get_items, delete_items
from core.storage import get_photo_path, delete_photo_files


class GalleryComponent:

    def __init__(self) -> None:
        # Dialog for review photo
        with (
            ui.dialog() as self.dialog,
            ui.card().classes("w-full max-w-xl p-2"),
        ):
            self.dialog_img = ui.image().classes("w-full")

        # Confirmation dialog
        with ui.dialog() as self.confirm_dialog, ui.card().classes("p-4 gap-4"):
            self.confirm_label = ui.label()
            ui.label(
                "Цю дію неможливо скасувати. Файли буде стерто з бази та диска."
            ).classes("text-sm text-gray-500")

            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Скасувати", on_click=self.confirm_dialog.close).props(
                    "flat"
                )
                ui.button(
                    "Видалити", color="negative", on_click=self.execute_delete
                ).props("unelevated")

        # For pagination
        self.has_more: bool = True
        self.next_offset = None

        # Select state
        self.selection_mode: bool = False
        self.selected_ids: set[str] = set()

        # Vidgets storage for update DOM
        self.cards: dict[str, ui.card] = {}
        self.card_path: dict[str, str] = {}

        # Interface (render)
        self.select_mode_btn: ui.button | None = None
        self.delete_btn: ui.button | None = None
        self.grid: ui.row | None = None
        self.load_more_btn: ui.button | None = None

        self.ACTIVE_CLASSES = "outline-4 outline-blue-500 scale-95"

    def confirm_delete(self) -> None:
        if not self.selected_ids:
            return
        self.confirm_label.text = (
            f"Видалити {len(self.selected_ids)} обраних фотографій?"
        )
        self.confirm_dialog.open()

    async def execute_delete(self) -> None:
        # 1. Delete from disk and qdrant storage 
        # 2. Delete vidgets 
        self.confirm_dialog.close()

        ids_to_delete = list(self.selected_ids)
        paths_to_delete = [
            self.card_path[item_id]
            for item_id in ids_to_delete
            if item_id in self.card_path
        ]

        await delete_items(ids_to_delete)
        delete_photo_files(paths_to_delete)

        for item_id in ids_to_delete:
            if card := self.cards.pop(item_id, None):
                card.delete()
            self.card_path.pop(item_id, None)

        self.selected_ids.clear()
        self._update_delete_btn()
        ui.notify(f"Успішно видалено {len(ids_to_delete)} фото", type="positive")

    def toggle_card_selection(self, item_id: str) -> None:
        card = self.cards.get(item_id)
        if not card:
            return

        if item_id in self.selected_ids:
            self.selected_ids.remove(item_id)
            card.classes(remove=self.ACTIVE_CLASSES)
        else:
            self.selected_ids.add(item_id)
            card.classes(add=self.ACTIVE_CLASSES)

        self._update_delete_btn()

    def toggle_selection_mode(self) -> None:
        """Batch mode for photo on/off"""
        self.selection_mode = not self.selection_mode
        self.selected_ids.clear()

        if self.select_mode_btn:
            self.select_mode_btn.text = (
                "Скасувати" if self.selection_mode else "Вибрати"
            )
            self.select_mode_btn.props(
                "color=grey" if self.selection_mode else "outline"
            )

        if not self.selection_mode:
            for card in self.cards.values():
                card.classes(remove=self.ACTIVE_CLASSES)

        self._update_delete_btn()

    def _update_delete_btn(self) -> None:
        if not self.delete_btn:
            return

        count = len(self.selected_ids)
        if count > 0:
            self.delete_btn.classes(remove="hidden")
            self.delete_btn.tooltip(f"Видалити {count} фото")
        else:
            self.delete_btn.classes(add="hidden")

    def _render_card(self, item: dict) -> None:
        item_id = item["id"]
        photo_path = item["photo_path"]
        image = get_photo_path(photo_path)

        with ui.card().tight().classes("no-shadow cursor-pointer") as card:
            self.cards[item_id] = card
            self.card_path[item_id] = photo_path

            ui.image(image).classes("w-40 aspect-square")

            card.on(
                "click",
                lambda: self.on_card_click(item_id, image),
            )

    def on_card_click(self, item_id: str, img_path) -> None:
        if self.selection_mode:
            self.toggle_card_selection(item_id)
        else:
            self.open_photo(img_path)

    async def load_photos(self) -> None:
        if not self.has_more or not self.grid:
            return

        items, self.next_offset = await get_items(
            limit=50, offset=self.next_offset
        )

        with self.grid:
            for item in items:
                self._render_card(item)

        if self.next_offset is None:
            self.has_more = False
            if self.load_more_btn:
                self.load_more_btn.set_visibility(False)
                ui.notify("Всі фото переглянуто", type="info")

    async def render(self) -> None:
        # 1. Buttons toolbar
        with ui.row().classes("w-full items-center justify-between px-2 mb-4"):
            ui.label("Галерея").classes("text-xl font-bold")

            with ui.row().classes("gap-2 items-center"):
                self.delete_btn = (
                    ui.button(icon="delete", on_click=self.confirm_delete)
                    .props("flat round color=negative")
                    .classes("hidden")
                )
                self.select_mode_btn = ui.button(
                    "Вибрати", on_click=self.toggle_selection_mode
                ).props("outline")

        # 2. Card grid 
        self.grid = ui.row().classes("gap-2 w-full")

        # 3. Pagination button
        with ui.row().classes("w-full justify-center mt-4"):
            self.load_more_btn = ui.button(
                "Завантажити більше", on_click=self.load_photos, icon="refresh"
            )

        # 4. Load photo 
        await self.load_photos()

    def open_photo(self, img_path):
        self.dialog_img.set_source(img_path)
        self.dialog.open()