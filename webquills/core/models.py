from pathlib import Path

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Collection, Page
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel
import wagtail.images.models as wagtail_images
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from webquills.core.blocks import BaseStreamBlock

image_model_name = get_image_model_string()


###############################################################################
# Ancillary models used by pages or exposed in CMS
###############################################################################
@register_setting
class SiteMeta(BaseSetting):
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
        default=settings.WAGTAIL_SITE_NAME,
        help_text=_("Owner of the copyright (in footer notice)"),
    )
    # TODO Add a License table and FK
    copyright_license_notice = RichTextField(
        _("copyright license notice"),
        default=_("All rights reserved."),
        help_text=_(
            "Text to follow the copyright notice indicating any license, e.g. CC-BY"
        ),
    )


def get_cta_template_path():
    # TODO Template should be in theme. Move after defining theme architecture.
    theme_path = settings.BASE_DIR / "webquills" / "core" / "templates"
    cta_path = theme_path / "webquills" / "cta"
    return cta_path


@register_snippet
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
    lead = StreamField(
        BaseStreamBlock(),
        verbose_name=_("lead paragraph"),
        blank=True,
        help_text=_("Paragraph leading reader to the action"),
    )
    picture = models.ForeignKey(
        wagtail_images.Image,
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
    landing_page = models.ForeignKey(
        Page,
        verbose_name=_("landing page"),
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        help_text=_(
            "CTA will either link/submit to a landing page on site, or to an external "
            "target URL. Choose only one."
        ),
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

    # Wagtail Admin
    panels = [
        FieldPanel("admin_name"),
        FieldPanel("headline"),
        FieldRowPanel(
            [
                PageChooserPanel("landing_page"),
                FieldPanel("target_url"),
            ],
            heading=_("Target page or URL"),
        ),
        FieldPanel("action_label"),
        StreamFieldPanel("lead"),
        ImageChooserPanel("picture"),
        FieldPanel("custom_template"),
    ]


class ArticleTag(TaggedItemBase):
    content_object = ParentalKey(
        "ArticlePage", related_name="tagged_items", on_delete=models.CASCADE
    )


###############################################################################
# Core Page types
###############################################################################
class HomePage(Page):
    """Site home page"""

    body = StreamField(BaseStreamBlock(), verbose_name="Page body", blank=True)
    cta = models.ForeignKey(
        CallToAction,
        verbose_name=_("call to action"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["featured_articles"] = (
            ArticlePage.objects.descendant_of(self)
            .live()
            .filter(tags__name="hpfeatured")
        )
        context["recent_articles"] = (
            ArticlePage.objects.descendant_of(self)
            .live()
            .order_by("-first_published_at")[:26]
        )
        return context

    @property
    def published(self):
        "Datetime of publication for copyright purposes"
        if self.live:
            return self.last_published_at
        return self.go_live_at

    @property
    def updated(self):
        "Datetime of the most recent significant editorial update"
        return self.published

    content_panels = Page.content_panels + [
        FieldPanel("cta"),
        StreamFieldPanel("body"),
    ]


class CategoryPage(Page):
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
    parent_page_types = ["webquills.HomePage"]
    subpage_types = ["webquills.ArticlePage"]  # Allow subcategories?

    intro = StreamField(BaseStreamBlock(), verbose_name=_("intro"), blank=True)
    featured_image = models.ForeignKey(
        image_model_name,
        verbose_name=_("featured image"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["featured_articles"] = (
            ArticlePage.objects.child_of(self).live().filter(tags__name="featured")
        )
        context["recent_articles"] = (
            ArticlePage.objects.child_of(self)
            .live()
            .order_by("-first_published_at")[:26]
        )
        return context

    @property
    def published(self):
        "Datetime of publication for copyright purposes"
        if self.live:
            return self.last_published_at
        return self.go_live_at

    @property
    def updated(self):
        "Datetime of the most recent significant editorial update"
        return self.published

    content_panels = Page.content_panels + [
        ImageChooserPanel("featured_image"),
        StreamFieldPanel("intro"),
    ]


class ArticlePage(Page):
    """## Article page
    The Article page is the primary container for content. Articles come in two
    flavors (we use the same model for both): sub-topics, and major topics. Sub-topic
    articles are brief (300–3,000 words) and cover a single niche subject. Major topic
    articles are long (5,000–20,000 words) and cover a broad topic in detail,
    comprising several sections with sub-heads.

    Sub-topic articles should be children of a category. Major topic articles may be
    children of a category page, or of the home page.
    """

    parent_page_types = ["webquills.HomePage", "webquills.CategoryPage"]
    subpage_types = []  # Articles do not have subpages

    # Stored database fields
    body = StreamField(
        BaseStreamBlock(),
        verbose_name=_("article body"),
        blank=True,
        help_text=_("Article text, excluding the headline (provided by 'title')"),
    )
    featured_image = models.ForeignKey(
        image_model_name,
        verbose_name=_("featured image"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    orig_published_at = models.DateTimeField(
        verbose_name=_("original publish date"),
        db_index=True,
        blank=True,
        null=True,
        help_text=_(
            "If published before being added to this site, set the original publish "
            "date here."
        ),
    )
    updated_at = models.DateTimeField(
        verbose_name=_("updated date"),
        db_index=True,
        blank=True,
        null=True,
        help_text=_("Date of the most recent significant editorial update, if any."),
    )
    tags = ClusterTaggableManager(through=ArticleTag, blank=True)

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

    @property
    def published(self):
        "Datetime of original publication"
        if self.live:
            return self.orig_published_at or self.first_published_at
        return self.go_live_at

    @property
    def updated(self):
        "Datetime of the most recent significant editorial update"
        return self.updated_at or self.published

    # Wagtail Admin Panels
    content_panels = Page.content_panels + [
        ImageChooserPanel("featured_image"),
        StreamFieldPanel("body"),
    ]

    settings_panels = [
        FieldRowPanel(
            [
                FieldPanel("orig_published_at"),
                FieldPanel("updated_at"),
            ],
            heading=_("Dates"),
        )
    ] + Page.settings_panels

    promote_panels = [FieldPanel("tags")] + Page.promote_panels