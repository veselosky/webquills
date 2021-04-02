from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

import wagtail.images.models as wagtail_images
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
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from webquills.core.blocks import BaseStreamBlock

image_model_name = get_image_model_string()


###############################################################################
# Site settings
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


###############################################################################
# Core Page types
###############################################################################
class HomePage(Page):
    """Site home page"""

    body = StreamField(BaseStreamBlock(), verbose_name="Page body", blank=True)

    content_panels = Page.content_panels + [StreamFieldPanel("body")]


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

    intro = StreamField(BaseStreamBlock(), verbose_name=_("intro"), blank=True)
    featured_image = models.ForeignKey(
        image_model_name,
        verbose_name=_("featured image"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    content_panels = Page.content_panels + [StreamFieldPanel("intro")]


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

    @property
    def published(self):
        "Datetime of original publication"
        return self.orig_published_at or self.first_published_at

    @property
    def attribution(self):
        "Article byline. Someday this will do something meaningful."
        return "by Vince Veselosky"

    content_panels = Page.content_panels + [
        StreamFieldPanel("body"),
        FieldPanel("featured_image"),
    ]
    settings_panels = Page.settings_panels + [
        FieldPanel("orig_published_at"),
    ]