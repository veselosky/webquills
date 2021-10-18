from contextlib import contextmanager
from pathlib import Path
import os

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField
from taggit.managers import TaggableManager

from .images import img_upload_to, fillcrop_image, resize_image, Thumb


###############################################################################
# Ancillary models used by pages or exposed in CMS
###############################################################################
ALL_RIGHTS_RESERVED = _("All rights reserved")


class CopyrightLicense(models.Model):
    class Meta:
        verbose_name = _("copyright license")
        verbose_name_plural = _("copyright licenses")

    name = models.CharField(
        _("name"),
        blank=False,
        max_length=50,
        help_text=_("A short name for use in the admin"),
    )
    notice = HTMLField(
        _("copyright license notice"),
        default=_("All rights reserved."),
        help_text=_("Text to follow the copyright notice indicating any license"),
    )
    url = models.CharField(
        _("copyright license URL"),
        blank=True,
        null=True,
        max_length=255,
        help_text=_(
            "Link to the full copyright license. Leave blank if the notice contains "
            "a link to the license. "
        ),
    )

    def __str__(self) -> str:
        return self.name


class AuthorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("copyright_license")


class Author(models.Model):
    """
    Author is a container for attribution and copyright information, not necessarily
    representing an actual person.
    """

    class Meta:
        verbose_name = _("author")
        verbose_name_plural = _("authors")

    objects = AuthorManager()

    byline = models.CharField(
        _("byline"),
        max_length=255,
        blank=True,
        help_text=_(
            "As in a newspaper byline, a name to attribute authorship of an article, "
            "e.g. 'Edward R. Murrow' (omit the word 'by')."
        ),
    )
    about = HTMLField(
        verbose_name=_("about"),
        blank=True,
        help_text=_(
            "A paragraph or two about the author. May include a headshot, links to "
            "the author's website, recent publications, etc. Typically displayed in "
            "article footer or sidebar. "
        ),
    )
    copyright_holder = models.CharField(
        _("copyright holder"),
        max_length=255,
        blank=True,
        help_text=_(
            "Name to use in copyright notice as owner, e.g. 'Galactic Media LLC'. If "
            "the material is not subject to copyright, or you don't want a default "
            "copyright notice printed, leave blank and explain in the copyright "
            "notice field. "
        ),
    )
    copyright_license = models.ForeignKey(
        CopyrightLicense,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_(
            "Select a standard license to apply, or leave blank for "
            "'All rights reserved'."
        ),
    )

    def __str__(self) -> str:
        return f"{self.byline} ({self.copyright_holder})"


class Copyrightable(models.Model):
    """
    Copyrightable objects have an optional link to Author, a container for copyright
    and attribution information. They also have custom fields to override the Author
    information where necessary and add additional attributions or credits.
    """

    class Meta:
        abstract = True

    author = models.ForeignKey(
        Author,
        verbose_name=_("author"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
    )
    credits = HTMLField(
        verbose_name=_("credits"),
        blank=True,
        help_text=_("Additional credits (typically displayed in footer or sidebar)"),
    )
    custom_byline = models.CharField(
        _("byline"),
        max_length=255,
        blank=True,
        help_text=_(
            "As in a newspaper byline, a name to attribute authorship of an article, "
            "e.g. 'Edward R. Murrow' (omit the word 'by')."
        ),
    )
    custom_about = HTMLField(
        verbose_name=_("about"),
        blank=True,
        help_text=_(
            "A paragraph or two about the author. May include a headshot, links to "
            "the author's website, recent publications, etc. Typically displayed in "
            "article footer or sidebar. "
        ),
    )
    custom_copyright_holder = models.CharField(
        _("copyright holder"),
        max_length=255,
        blank=True,
        help_text=_(
            "Name to use in copyright notice as owner, e.g. 'Galactic Media LLC'. If "
            "the material is not subject to copyright, or you don't want a default "
            "copyright notice printed, leave blank and explain in the copyright "
            "notice field. "
        ),
    )
    custom_copyright_license = models.ForeignKey(
        CopyrightLicense,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_(
            "Select a standard license to apply, or leave blank to use the site "
            "default. "
        ),
    )
    custom_copyright_notice = HTMLField(
        verbose_name=_("copyright notice"),
        blank=True,
        help_text=_("A custom copyright notice to replace the default. "),
    )

    @property
    def byline(self):
        if self.custom_byline:
            return self.custom_byline
        if self.author and self.author.byline:
            return self.author.byline
        try:
            return self.site.author.byline
        except AttributeError:
            pass
        return ""

    @property
    def about(self):
        if self.custom_about:
            return self.custom_about
        if self.author and self.author.about:
            return self.author.about
        try:
            return self.site.author.about
        except AttributeError:
            pass
        return ""

    @property
    def copyright_holder(self):
        if self.custom_copyright_holder:
            return self.custom_copyright_holder
        if self.author and self.author.copyright_holder:
            return self.author.copyright_holder
        try:
            return self.site.author.copyright_holder
        except AttributeError:
            pass
        return ""

    @property
    def copyright_license(self):
        if self.custom_copyright_license:
            return self.custom_copyright_license
        if self.author and self.author.copyright_license:
            return self.author.copyright_license
        try:
            return self.site.author.copyright_license
        except AttributeError:
            pass
        return None

    @property
    def copyright_notice(self):
        if self.custom_copyright_notice:
            return self.custom_copyright_notice
        tpl = _("© Copyright %(year)s %(owner)s ")
        notice = tpl % {"year": self.copyright_year, "owner": self.copyright_holder}
        if self.copyright_license:
            notice += self.copyright_license.notice
        else:
            notice += ALL_RIGHTS_RESERVED
        return notice

    @property
    def copyright_year(self):
        "Subclasses should implement their own copyright year"
        return timezone.now().year


###############################################################################
# The Image model
###############################################################################
class Image(Copyrightable, models.Model):
    class Meta:
        verbose_name = _("image")
        verbose_name_plural = _("images")
        ordering = ["-created_at"]
        get_latest_by = "created_at"

    name = models.CharField(max_length=255, verbose_name=_("name"))
    file = models.ImageField(
        verbose_name=_("file"),
        upload_to=img_upload_to,
        width_field="width",
        height_field="height",
    )
    site = models.ForeignKey(
        "sites.Site",
        on_delete=models.PROTECT,
        verbose_name=_("site"),
        help_text=_(
            "Note: images are associated with a site, but are physically "
            "shared among all sites. "
        ),
    )
    width = models.IntegerField(verbose_name=_("width"), editable=False)
    height = models.IntegerField(verbose_name=_("height"), editable=False)
    alt_text = models.CharField(_("alt text"), blank=True, max_length=255)
    created_at = models.DateTimeField(
        verbose_name=_("created at"), auto_now_add=True, db_index=True
    )
    copyright_date = models.DateField(
        verbose_name=_("copyright year"), blank=True, null=True
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
    def copyright_year(self):
        return self.copyright_date.year

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


###############################################################################
# Core Page types
###############################################################################
class Status(models.TextChoices):
    WITHHELD = "withheld", _("Draft (withheld)")
    USABLE = "usable", _("Publish (usable)")
    CANCELLED = "cancelled", _("Unpublish (cancelled)")


class PageManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related(
                "site", "author", "featured_image", "custom_copyright_license"
            )
        )

    def live(self):
        return self.get_queryset().filter(
            models.Q(expired__isnull=True) | models.Q(expired__gt=timezone.now()),
            status=Status.USABLE,
            published__lte=timezone.now(),
        )


class AbstractPage(Copyrightable, models.Model):
    class Meta:
        abstract = True

    objects = PageManager()

    # Common fields for all pages
    site = models.ForeignKey(
        "sites.Site",
        on_delete=models.PROTECT,
        verbose_name=_("site"),
        related_name="%(class)ss",
    )
    seo_title = models.CharField(_("page title"), max_length=255, blank=True)
    seo_description = models.CharField(_("description"), max_length=255, blank=True)
    headline = models.CharField(_("headline"), max_length=255)
    slug = models.SlugField(_("slug"))
    featured_image = models.ForeignKey(
        Image,
        verbose_name=_("featured image"),
        related_name="+",  # images don't point back
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    status = models.CharField(
        _("status"),
        max_length=50,
        choices=Status.choices,
        default=Status.WITHHELD,
        db_index=True,
        help_text=_("Controls visibility (must be Published/Usable to be visible)."),
    )
    published = models.DateTimeField(
        _("published"),
        blank=False,
        null=False,
        default=timezone.now,
        db_index=True,
        help_text=_(
            "Publication date for copyright purposes. Also controls visibility (must "
            "be published in the past to be visible)."
        ),
    )
    updated_at = models.DateTimeField(
        _("updated"), auto_now=False, auto_now_add=False, blank=True, null=True
    )
    expired = models.DateTimeField(
        _("expired"),
        blank=True,
        null=True,
        db_index=True,
        help_text=_(
            "Time after which the content is no longer valid. Controls visibility "
            "(expired, if set, must be in the future to be visible)."
        ),
    )
    tags = TaggableManager(blank=True)

    @property
    def copyright_year(self):
        return self.published.year

    @property
    def title(self):
        return self.seo_title or self.headline

    @property
    def updated(self):
        if self.updated_at:
            return self.updated_at
        return self.published

    def __str__(self):
        return self.headline


class HomePage(AbstractPage):
    class Meta:
        verbose_name = _("home page")
        verbose_name_plural = _("home pages")
        ordering = ["-published"]
        get_latest_by = "published"

    lead = HTMLField(
        verbose_name=_("lead paragraph"),
        blank=True,
        help_text=_("Paragraph leading reader to the action."),
    )
    picture = models.ForeignKey(
        Image,
        verbose_name=_("picture"),
        related_name="+",  # images don't point back
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    action_label = models.CharField(
        _("action label"),
        max_length=50,
        default=_("Learn more"),
        help_text=_("The label on the action button or link"),
    )
    target_url = models.URLField(
        _("target URL"),
        blank=True,
        null=True,
        help_text=_(
            "CTA will either link/submit to a landing page on site, or to an external "
            "target URL. Choose only one."
        ),
    )

    def get_absolute_url(self):
        return reverse("home")

    def get_template(self):
        return "webquills/home_page.html"


class CategoryPage(AbstractPage):
    class Meta:
        verbose_name = _("category page")
        verbose_name_plural = _("category pages")
        ordering = ["site", "menu_order"]
        get_latest_by = "published"
        indexes = [models.Index(fields=["site", "menu_order"])]

    intro = HTMLField(
        verbose_name=_("intro"),
        blank=True,
    )

    menu_order = models.PositiveSmallIntegerField(
        verbose_name=_("menu order"),
        default=0,
    )

    def get_absolute_url(self):
        return reverse("category", kwargs={"category_slug": self.slug})

    def get_template(self):
        return "webquills/category_page.html"


class ArticleManager(PageManager):
    def get_queryset(self):
        return super().get_queryset().select_related("category")


class ArticlePage(AbstractPage):
    class Meta:
        verbose_name = _("article page")
        verbose_name_plural = _("article pages")
        ordering = ["-published"]
        get_latest_by = "published"

    # Stored database fields
    category = models.ForeignKey(
        CategoryPage, verbose_name=_("category"), on_delete=models.PROTECT
    )
    body = HTMLField(
        verbose_name=_("article body"),
        blank=True,
        help_text=_("Article text, excluding the headline (provided by 'title'). "),
    )
    objects = ArticleManager()

    # Additional properties and methods
    @property
    def excerpt(self):
        """Rich text excerpt for use in teases and feed content. If no excerpt has
        been specified, returns the full body text."""
        if not self.body:
            return ""
        excerpt = self.body.split(
            settings.TINYMCE_DEFAULT_CONFIG["pagebreak_separator"], maxsplit=1
        )[0]
        return excerpt

    def get_absolute_url(self):
        return reverse(
            "article",
            kwargs={"category_slug": self.category.slug, "article_slug": self.slug},
        )

    def get_template(self):
        return "webquills/article_page.html"
