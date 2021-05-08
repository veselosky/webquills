from dataclasses import dataclass
from pathlib import Path
import os
import tempfile

from django.apps import apps
from django.conf import settings
from django.core.files.images import ImageFile
from django.utils.translation import gettext_lazy as _
import PIL as pillow


###############################################################################
# Image model and related stuff
###############################################################################
def img_upload_to(instance, filename):
    """
    Calculate the upload destination for an image file.
    """
    config = apps.get_app_config("webquills")
    folder_name = config.get_image_media_dir()
    filename = Path(filename).name
    filename = instance.file.field.storage.get_valid_name(filename)

    # Truncate filename so it fits in the 100 character limit
    # https://code.djangoproject.com/ticket/9893
    full_path = os.path.join(folder_name, filename)
    if len(full_path) >= 95:
        chars_to_trim = len(full_path) - 94
        prefix, extension = os.path.splitext(filename)
        filename = prefix[:-chars_to_trim] + extension
        full_path = os.path.join(folder_name, filename)

    return full_path


# instance may be passed as positional, other kwargs are keyword-only
def resize_image(instance: "Image", *, width: int = None, height: int = None):
    "Generate a resized version of Image maintaining the same aspect ratio"
    app = apps.get_app_config("webquills")
    op_name = "resize"
    imagedir = app.get_image_media_dir()

    # We know the op_name, now work out the arguments

    # Called without a size, use our default size.
    if width is None and height is None:
        width, height = app.get_default_image_size()

    # Called with only one, calculate the other based on aspect ratio
    if width is None or height is None:
        aspect_ratio = instance.width / instance.height
        if height:
            width = int(height * aspect_ratio)
        else:
            height = int(width / aspect_ratio)

    # If the image already fits in the box, just return it, don't upscale
    if instance.width < width and instance.height < height:
        return instance.file.name

    storage = instance.file.storage
    newname = instance.file.name.replace(imagedir, f"img-{op_name}-{width}x{height}")
    newname = storage.generate_filename(newname)

    with instance.open_file() as img_file:
        image = pillow.Image.open(img_file).copy()  # open original image
        image.thumbnail([width, height])  # transform in memory
        # Store to local file. Suffix needed for img format detection
        tmpfile = tempfile.NamedTemporaryFile(
            "wb", delete=False, suffix=Path(newname).suffix
        )
        image.save(tmpfile, format=image.format)
        # To reopen, some platforms require close
        # https://docs.python.org/3.8/library/tempfile.html#tempfile.NamedTemporaryFile
        tmpfile.close()
        # Hand the tmpfile to the image storage. Must have valid img suffix e.g. .jpg
        saved_as = storage.save(newname, ImageFile(open(tmpfile.name, "rb")))

    return saved_as


def fillcrop_image(instance: "Image", *, width: int, height: int):
    "Generate a resized version of Image cropped to the specified aspect ratio"
    app = apps.get_app_config("webquills")
    op_name = "fillcrop"
    imagedir = app.get_image_media_dir()

    # If the image already fits in the box, just return it, don't upscale
    if instance.width < width and instance.height < height:
        return instance.file.name

    storage = instance.file.storage
    newname = instance.file.name.replace(imagedir, f"img-{op_name}-{width}x{height}")
    newname = storage.generate_filename(newname)

    with instance.open_file() as img_file:
        image = pillow.Image.open(img_file).copy()  # open original image

        target_aspect = width / height
        if instance.aspect_ratio > target_aspect:
            # src is wider, so fit the height and crop the width
            temp_width = int(height * instance.aspect_ratio)
            image.thumbnail([temp_width, height])  # transform in memory
            x = int((temp_width - width) / 2)  # crop from center
            image = image.crop([x, 0, x + width, height])
        else:
            # dest is wider, fit the width and crop the height
            temp_height = int(width / instance.aspect_ratio)
            image.thumbnail([width, temp_height])  # transform in memory
            y = int((temp_height - height) / 2)  # crop from center
            image = image.crop([0, y, width, y + height])

        # Store to local file. Suffix needed for img format detection
        tmpfile = tempfile.NamedTemporaryFile(
            "wb", delete=False, suffix=Path(newname).suffix
        )
        image.save(tmpfile, format=image.format)
        # To reopen, some platforms require close
        # https://docs.python.org/3.8/library/tempfile.html#tempfile.NamedTemporaryFile
        tmpfile.close()
        # Hand the tmpfile to the image storage. Must have valid img suffix e.g. .jpg
        saved_as = storage.save(newname, ImageFile(open(tmpfile.name, "rb")))

    return saved_as


@dataclass
class Thumb:
    "A helper class representing a transformed image."
    op: str
    kwargs: dict
    path: str = ""

    @property
    def url(self) -> str:
        return settings.MEDIA_URL + self.path
