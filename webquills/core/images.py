from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import os
import tempfile

from django.apps import apps
from django.conf import settings
from django.core.files.images import ImageFile
from django.db import models
from django.utils.translation import gettext_lazy as _
import PIL as pillow
from taggit.managers import TaggableManager


###############################################################################
# Image model and related stuff
###############################################################################
def get_upload_to(instance, filename):
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


class Image(models.Model):
    class Meta:
        verbose_name = _("image")
        verbose_name_plural = _("images")
        ordering = ["-created_at"]
        get_latest_by = "created_at"

    name = models.CharField(max_length=255, verbose_name=_("name"))
    file = models.ImageField(
        verbose_name=_("file"),
        upload_to=get_upload_to,
        width_field="width",
        height_field="height",
    )
    width = models.IntegerField(verbose_name=_("width"), editable=False)
    height = models.IntegerField(verbose_name=_("height"), editable=False)
    alt_text = models.CharField(_("alt text"), blank=True, max_length=255)
    created_at = models.DateTimeField(
        verbose_name=_("created at"), auto_now_add=True, db_index=True
    )
    uploaded_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("uploaded by user"),
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL,
    )

    tags = TaggableManager(help_text=None, blank=True, verbose_name=_("tags"))

    focal_point_x = models.PositiveIntegerField(null=True, blank=True)
    focal_point_y = models.PositiveIntegerField(null=True, blank=True)
    focal_point_width = models.PositiveIntegerField(null=True, blank=True)
    focal_point_height = models.PositiveIntegerField(null=True, blank=True)

    file_size = models.PositiveIntegerField(null=True, editable=False)
    thumbs = models.JSONField(
        _("thumbnails"),
        default=list,  # New list each time, not shared among all instances!
        blank=True,
        help_text=_("Resized versions of the image that have been generated"),
    )

    def save(self, *args, **kwargs) -> None:
        """
        Overridden to keep some fields up to date with the underlying file. Note that
        Django itself populates the width and height fields.

        See also post_save signals wired in apps.py for thumbnail generation.
        """
        self.file_size = self.file.size
        return super().save(*args, **kwargs)

    # params after op MUST be passed as kwargs
    def get_thumb(self, op: str, **kwargs) -> Thumb:
        """
        Given `op` (operation) and `kwargs`, return the path (relative to MEDIA_ROOT) of
        an image file that has been transformed with the given op and kwargs.
        """
        found = list(
            filter(lambda x: x["op"] == op and x["kwargs"] == kwargs, self.thumbs)
        )
        if found:  # just return, don't check if it exists
            return Thumb(**found[0])

        # Currently only support 2 ops, make a registry if you want to add more
        if op == "resize":
            newpath = resize_image(self, **kwargs)
        elif op == "fillcrop":
            newpath = fillcrop_image(self, **kwargs)
        else:
            raise ValueError(f"Invalid image op: {op}")
        # Cache the generated thumb's path for future use
        thumb = {"op": op, "kwargs": kwargs, "path": newpath}
        self.thumbs.append(thumb)
        self.save(update_fields=["thumbs"])

        return Thumb(**thumb)

    def is_stored_locally(self):
        """
        Returns True if the image is hosted on the local filesystem
        """
        try:
            self.file.path

            return True
        except NotImplementedError:
            return False

    @property
    def is_portrait(self):
        return self.width < self.height

    @property
    def is_landscape(self):
        return self.height < self.width

    @property
    def aspect_ratio(self):
        return self.width / self.height

    @property
    def basename(self):
        return os.path.basename(self.file.name)

    @property
    def original(self):
        "Return URL of the original image as uploaded."
        return self.file.url

    def __str__(self) -> str:
        return self.name

    @contextmanager
    def open_file(self):
        # Open file if it is closed
        close_file = False
        image_file = self.file

        if self.file.closed:
            # Reopen the file
            if self.is_stored_locally():
                self.file.open("rb")
            else:
                # Some external storage backends don't allow reopening
                # the file. Get a fresh file instance. #1397
                storage = self._meta.get_field("file").storage
                image_file = storage.open(self.file.name, "rb")

            close_file = True

        # Seek to beginning
        image_file.seek(0)

        try:
            yield image_file
        finally:
            if close_file:
                image_file.close()
