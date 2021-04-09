import os
from pathlib import Path

from django.conf import settings
from django.db import models
from django.utils import timezone, text
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField
from taggit.managers import TaggableManager


###############################################################################
# Image model and related stuff
###############################################################################
def get_upload_to(instance, filename):
    """
    Calculate the upload destination for an image file.
    """
    folder_name = "uploads"
    filename = text.slugify(filename, allow_unicode=False)
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


class Image(models.Model):
    """
    The Webquills Image model is largely cribbed from Wagtail's Image.
    """

    class Meta:
        pass

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

    def save(self, *args, **kwargs) -> None:
        """
        Overridden to keep some fields up to date with the underlying file. Note that
        Django itself populates the width and height fields.
        """
        self.file_size = self.file.size
        return super().save(*args, **kwargs)

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
    def basename(self):
        return os.path.basename(self.file.name)


###############################################################################
# Ancillary models used by pages or exposed in CMS
###############################################################################
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
    copyright_license_notice = HTMLField(
        _("copyright license notice"),
        default=_("All rights reserved."),
        help_text=_("Text to follow the copyright notice indicating any license"),
    )
    copyright_license_url = models.CharField(
        _("copyright license URL"),
        blank=True,
        null=True,
        max_length=255,
        help_text=_("Link to the full copyright license"),
    )


# TODO custom manager with select_related(copyright_license)
class SiteMeta(models.Model):
    class Meta:
        verbose_name = _("site metadata")
        verbose_name_plural = _("site metadata")

    site = models.OneToOneField(
        "sites.Site", on_delete=models.CASCADE, primary_key=True
    )
    tagline = models.CharField(
        _("tagline"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Subtitle. A few words letting visitors know what to expect."),
    )
    copyright_holder = models.CharField(
        _("copyright holder"),
        max_length=255,
        default="WebQuills",
        help_text=_("Owner of the copyright (in footer notice)"),
    )
    copyright_license = models.ForeignKey(
        CopyrightLicense,
        on_delete=models.SET_NULL,
        verbose_name=_("copyright license"),
        blank=True,
        null=True,
    )


def get_cta_template_path():
    # TODO Template should be in theme. Move after defining theme architecture.
    theme_path = settings.BASE_DIR / "webquills" / "core" / "templates"
    cta_path = theme_path / "webquills" / "cta"
    return cta_path


class CallToAction(models.Model):
    "A home page module calling visitor to take an important action"

    class Meta:
        verbose_name_plural = _("calls to action")

    admin_name = models.CharField(
        _("admin name"),
        max_length=255,
        unique=True,
        help_text=_(
            "A unique name to be displayed in the admin (not visible to the public)"
        ),
    )

    headline = models.CharField(_("headline"), max_length=255, blank=False, null=False)
    lead = HTMLField(
        verbose_name=_("lead paragraph"),
        blank=True,
        help_text=_("Paragraph leading reader to the action."),
    )
    picture = models.ForeignKey(
        Image,
        verbose_name=_("picture"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    action_label = models.CharField(
        _("action label"),
        max_length=50,
        blank=False,
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
    custom_template = models.FilePathField(
        verbose_name=_("custom template"),
        path=get_cta_template_path,
        max_length="255",
        default=str(get_cta_template_path() / "jumbolink.html"),
        help_text=_("Template used to render the CTA"),
    )

    def __str__(self) -> str:
        return self.admin_name

    @property
    def template(self):
        theme_path = settings.BASE_DIR / "webquills" / "core" / "templates"
        return str(Path(self.custom_template).relative_to(theme_path))

    @property
    def link(self):
        return self.target_url or self.landing_page.get_url()


class Status(models.TextChoices):
    WITHHELD = "withheld", _("Draft (withheld)")
    USABLE = "usable", _("Publish (usable)")
    CANCELLED = "cancelled", _("Unpublish (cancelled)")


###############################################################################
# Core Page types
###############################################################################
class PageManager(models.Manager):
    def live(self):
        return self.filter(
            models.Q(expired__isnull=True) | models.Q(expired__gt=timezone.now()),
            status=Status.USABLE,
            published__lte=timezone.now(),
        )


class AbstractPage(models.Model):
    class Meta:
        abstract = True

    objects = PageManager()

    # Common fields for all pages
    seo_title = models.CharField(_("page title"), max_length=255, blank=True)
    seo_description = models.CharField(_("description"), max_length=255, blank=True)
    headline = models.CharField(_("headline"), max_length=255)

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

    @property
    def title(self):
        return self.seo_title or self.headline

    def __str__(self):
        return self.name


class HomePage(AbstractPage):
    """Site home page"""

    cta = models.ForeignKey(
        CallToAction,
        verbose_name=_("call to action"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )


class CategoryPage(AbstractPage):
    """## Category index page
    The category index page is a list page listing articles in a category (children of
    the category page) in reverse chronological order. It may have a featured section
    at the top for featured or "sticky" articles. The page intro appears above the
    featured section as an introduction to the category. The page body is not editable,
    but provides a list of child pages.

    Category pages appear in the site menu by default. There should be few of them,
    each covering a broad topic. They must be parented to the home page.
    """

    show_in_menus_default = True

    intro = HTMLField(
        verbose_name=_("intro"),
        blank=True,
    )
    featured_image = models.ForeignKey(
        Image,
        verbose_name=_("featured image"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )


class ArticlePage(AbstractPage):
    """## Article page
    The Article page is the primary container for content. Articles come in two
    flavors (we use the same model for both): sub-topics, and major topics. Sub-topic
    articles are brief (300–3,000 words) and cover a single niche subject. Major topic
    articles are long (5,000–20,000 words) and cover a broad topic in detail,
    comprising several sections with sub-heads.

    Sub-topic articles should be children of a category. Major topic articles may be
    children of a category page, or of the home page.
    """

    # Stored database fields
    body = HTMLField(
        verbose_name=_("article body"),
        blank=True,
        help_text=_("Article text, excluding the headline (provided by 'title'). "),
    )
    featured_image = models.ForeignKey(
        Image,
        verbose_name=_("featured image"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    # Additional properties and methods
    @property
    def attribution(self):
        "Article byline. Someday this will do something meaningful."
        return "by Vince Veselosky"

    @property
    def excerpt(self):
        "Rich text excerpt for use in teases and feed content."
        # By convention, use the first block of the body if it is a text block.
        if (
            self.body
            and self.body[0].block_type == "tease"
            or self.body[0].block_type == "text"
        ):
            return self.body[0]
        return self.search_description
