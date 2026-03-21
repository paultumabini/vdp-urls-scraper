from io import BytesIO
from pathlib import Path

from django.core.files import File
from PIL import Image

image_types = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "gif": "GIF",
    "tif": "TIFF",
    "tiff": "TIFF",
}


def image_resize(image, width, height):

    img = Image.open(image)

    if img.width > width or img.height > height:
        output_size = (width, height)
        img.thumbnail(output_size, Image.ANTIALIAS)
        img_filename = Path(image.file.name).name
        img_suffix = Path(image.file.name).name.split(".")[-1]
        img_format = image_types[img_suffix]
        buffer = BytesIO()
        img.save(buffer, format=img_format)
        file_object = File(buffer)

        # Save the new resized file as usual, which will save to S3 using django-storages
        image.save(img_filename, file_object)
