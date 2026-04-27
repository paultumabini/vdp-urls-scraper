from io import BytesIO
from pathlib import Path

from django.core.files import File
from PIL import Image

IMAGE_TYPES = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "gif": "GIF",
    "tif": "TIFF",
    "tiff": "TIFF",
}


def image_resize(image, width, height):
    """
    Resize an uploaded image in memory if it exceeds dimensions.
    """
    img = Image.open(image)

    if img.width > width or img.height > height:
        # LANCZOS gives high-quality downscaling for profile thumbnails.
        img.thumbnail((width, height), Image.Resampling.LANCZOS)
        img_filename = Path(image.file.name).name
        # Preserve original extension mapping; fallback prevents unknown type crashes.
        img_suffix = Path(image.file.name).suffix.lower().lstrip(".")
        img_format = IMAGE_TYPES.get(img_suffix, "JPEG")
        buffer = BytesIO()
        img.save(buffer, format=img_format)
        buffer.seek(0)
        file_object = File(buffer)

        # Persist through Django storage backend (local/S3/etc).
        image.save(img_filename, file_object)
