from pathlib import Path

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField
from taggit.managers import TaggableManager

from .images import Image


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


class SiteMetaManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("copyright_license")


class SiteMeta(models.Model):
    class Meta:
        verbose_name = _("site metadata")
        verbose_name_plural = _("site metadata")

    site = models.OneToOneField(
        "sites.Site", on_delete=models.CASCADE, primary_key=True, related_name="meta"
    )
    name = models.CharField(_("name"), max_length=50)
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
    objects = SiteMetaManager()


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
    site = models.ForeignKey(
        "sites.Site",
        on_delete=models.PROTECT,
        verbose_name=_("site"),
        related_name="ctas",
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

    cta = models.ForeignKey(
        CallToAction,
        verbose_name=_("call to action"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def get_absolute_url(self):
        return reverse("home")

    def get_template(self):
        return "webquills/home_page.html"


class CategoryPage(AbstractPage):
    class Meta:
        verbose_name = _("category page")
        verbose_name_plural = _("category pages")
        ordering = ["-published"]
        get_latest_by = "published"

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

    def get_absolute_url(self):
        return reverse("category", kwargs={"category_slug": self.slug})

    def get_template(self):
        return "webquills/category_page.html"


class ArticleManager(PageManager):
    def get_queryset(self):
        return super().get_queryset().select_related("category", "featured_image")


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
    featured_image = models.ForeignKey(
        Image,
        verbose_name=_("featured image"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    objects = ArticleManager()

    # Additional properties and methods
    @property
    def attribution(self):
        "Article byline. Someday this will do something meaningful."
        return "by Vince Veselosky"

    @property
    def excerpt(self):
        "Rich text excerpt for use in teases and feed content."
        # TODO Implement rich excerpt from article body
        return self.seo_description

    def get_absolute_url(self):
        return reverse(
            "article",
            kwargs={"category_slug": self.category.slug, "article_slug": self.slug},
        )

    def get_template(self):
        return "webquills/article_page.html"
