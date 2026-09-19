import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "data" / "reference"

def save_photo_bytes(image_bytes: bytes, extension: str = ".jpg") -> tuple[str, str]:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    photo_uuid = str(uuid.uuid7())
    file_name = f"{photo_uuid}{extension}"
    (STORAGE_DIR / file_name).write_bytes(image_bytes)

    return photo_uuid, file_name

def get_photo_path(file_name: str) -> Path:
    return STORAGE_DIR / file_name

def delete_photo_files(photo_paths: list[str]) -> None:
    for path in photo_paths:
        target = get_photo_path(path)
        target.unlink(missing_ok=True)
        