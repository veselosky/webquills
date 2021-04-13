from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.files.images import ImageFile
from django.test import TestCase
import PIL as pillow

from webquills.core.images import Image, resize_image, fillcrop_image


class TestImageModel(TestCase):
    def test_image_autofields(self):
        "Image.file_size should be auto-populated on save"
        here = Path(__file__).parent
        image_file = here / "cathryn-lavery-fMD_Cru6OTk-unsplash.jpg"
        # Create a temp dir to act as our MEDIA_ROOT during testing
        media_root = TemporaryDirectory()
        with self.settings(MEDIA_ROOT=media_root.name):
            with image_file.open("rb") as im:
                img = Image(file=ImageFile(im), name=image_file.name)
                img.save()

                assert img.file_size == img.file.size

    @patch("webquills.core.images.resize_image")
    def test_get_thumb(self, resizer):
        width = 600
        height = 400
        name = "test_image.jpg"
        resizer.return_value = f"img-r-{width}-{height}/{name}"

        here = Path(__file__).parent
        image_file = here / "cathryn-lavery-fMD_Cru6OTk-unsplash.jpg"
        # Create a temp dir to act as our MEDIA_ROOT during testing
        media_root = TemporaryDirectory()
        with self.settings(MEDIA_ROOT=media_root.name):
            with image_file.open("rb") as im:
                img = Image(file=ImageFile(im), name=name)
                img.save()

                resp = img.get_thumb("resize", width=width, height=height)
                # should have called func with width and height
                assert resizer.called_once_with(img, width=width, height=height)
                # should return the path we gave it
                assert resp == resizer.return_value
                # should save in its thumbs field
                assert img.thumbs[0] == {
                    "op": "resize",
                    "kwargs": {"width": width, "height": height},
                    "path": resizer.return_value,
                }
                # Should return cached version, NOT call resizer a second time
                resp = img.get_thumb("resize", width=width, height=height)
                resizer.assert_called_once()

    def test_resize_image_all_args(self):
        width = 600
        height = 400
        name = "test_image.jpg"
        here = Path(__file__).parent
        image_file = here / "cathryn-lavery-fMD_Cru6OTk-unsplash.jpg"
        # Create a temp dir to act as our MEDIA_ROOT during testing
        media_root = TemporaryDirectory()
        with self.settings(MEDIA_ROOT=media_root.name):
            with image_file.open("rb") as im:
                img = Image(file=ImageFile(im), name=name)
                img.save()

                # TEST BEGINS
                result = resize_image(img, width=width, height=height)
                result_file = Path(media_root.name) / result
                assert result_file.exists()
                assert result_file.stat().st_size > 0
                with pillow.Image.open(result_file) as test_img:
                    # Portrait, should have width exactly 600
                    assert test_img.width == width
                    assert test_img.height <= height

    def test_fillcrop_image_portrait(self):
        width = 400
        height = 600
        name = "test_image.jpg"
        here = Path(__file__).parent
        image_file = here / "cathryn-lavery-fMD_Cru6OTk-unsplash.jpg"
        # Create a temp dir to act as our MEDIA_ROOT during testing
        media_root = TemporaryDirectory()
        with self.settings(MEDIA_ROOT=media_root.name):
            with image_file.open("rb") as im:
                img = Image(file=ImageFile(im), name=name)
                img.save()

                # TEST BEGINS
                result = fillcrop_image(img, width=width, height=height)
                result_file = Path(media_root.name) / result
                assert result_file.exists()
                assert result_file.stat().st_size > 0
                with pillow.Image.open(result_file) as test_img:
                    # fillcrop dimensions should match exactly
                    assert test_img.width == width
                    assert test_img.height == height

    def test_fillcrop_image_landscape(self):
        width = 600
        height = 100
        name = "test_image.jpg"
        here = Path(__file__).parent
        image_file = here / "cathryn-lavery-fMD_Cru6OTk-unsplash.jpg"
        # Create a temp dir to act as our MEDIA_ROOT during testing
        media_root = TemporaryDirectory()
        with self.settings(MEDIA_ROOT=media_root.name):
            with image_file.open("rb") as im:
                img = Image(file=ImageFile(im), name=name)
                img.save()

                # TEST BEGINS
                result = fillcrop_image(img, width=width, height=height)
                result_file = Path(media_root.name) / result
                assert result_file.exists()
                assert result_file.stat().st_size > 0
                with pillow.Image.open(result_file) as test_img:
                    # fillcrop dimensions should match exactly
                    assert test_img.width == width
                    assert test_img.height == height
