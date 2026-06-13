from pathlib import Path
import uuid

from config.settings import BASE_DIR, CHAT_UPLOADS_DIR, PRODUCT_IMAGES_DIR


ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024


class ImageStorageService:
    def save_product_image(self, uploaded_file, store_id: int, product_db_id: int) -> str:
        return _save_image(uploaded_file, PRODUCT_IMAGES_DIR, f"store_{store_id}_product_{product_db_id}")

    def save_chat_image(self, uploaded_file) -> str:
        return _save_image(uploaded_file, CHAT_UPLOADS_DIR, "chat_upload")

    def delete_image(self, relative_path: str | None) -> None:
        if not relative_path:
            return

        path = _safe_absolute_path(relative_path)
        if path is None or not path.exists() or not path.is_file():
            return

        path.unlink()


def _save_image(uploaded_file, target_dir: Path, prefix: str) -> str:
    _validate_uploaded_image(uploaded_file)
    target_dir.mkdir(parents=True, exist_ok=True)

    extension = _extension(uploaded_file.name)
    file_name = f"{prefix}_{uuid.uuid4().hex}.{extension}"
    file_path = target_dir / file_name
    file_path.write_bytes(uploaded_file.getvalue())
    return file_path.relative_to(BASE_DIR).as_posix()


def _validate_uploaded_image(uploaded_file) -> None:
    if uploaded_file is None:
        raise ValueError("No image file selected.")

    extension = _extension(uploaded_file.name)
    if extension not in ALLOWED_IMAGE_EXTENSIONS or uploaded_file.type not in ALLOWED_IMAGE_MIME_TYPES:
        raise ValueError("Unsupported image type. Use JPG, JPEG, PNG, or WEBP.")

    size = getattr(uploaded_file, "size", None)
    if size is None:
        size = len(uploaded_file.getvalue())
    if size > MAX_IMAGE_SIZE_BYTES:
        raise ValueError("Image is too large. Maximum size is 5 MB.")


def _extension(file_name: str) -> str:
    return Path(file_name or "").suffix.lower().lstrip(".")


def _safe_absolute_path(relative_path: str) -> Path | None:
    candidate = (BASE_DIR / relative_path).resolve()
    base = BASE_DIR.resolve()
    if base not in candidate.parents and candidate != base:
        return None
    return candidate
