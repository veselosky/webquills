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
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Collection, Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from webquills.core.blocks import BaseStreamBlock


###############################################################################
# Core snippets
# Since WebQuills is a multi-tenant system, all Snippets should be scoped to a
# site, and are not intended to be shared across sites. Multi-tenancy is still
# only partially supported by Wagtail.
###############################################################################
@register_snippet
class FooterText(models.Model):
    """
    This provides editable text for the site footer.
    `register_snippet` allows it to be accessible via the admin. It is made
    accessible on the template via a template tag defined in navigation_tags.py
    """

    body = RichTextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "footer text"


@register_snippet
class Provider(models.Model):
    """
    Provider is a person or organization that provides access to content
    through syndication, for example a website like Unsplash.com or a news
    organization like the Associated Press.
    """

    name = models.CharField(_("provider name"), max_length=255)

    class Meta:
        verbose_name = _("provider")
        verbose_name_plural = _("providers")

    def __str__(self):
        return self.name


@register_snippet
class Attribution(models.Model):
    """
    Attributions store byline and copyright information.
    """

    class Meta:
        verbose_name = _("attribution")
        verbose_name_plural = _("attributions")

    admin_name = models.CharField(
        _("administrative name"),
        max_length=255,
        unique=True,
        help_text=_(
            "An internal name for this attribution, not visible to the public. "
            "Typically this will be the psuedonym or copyright holder. "
        ),
    )
    copyright_holder = models.CharField(
        _("copyright holder"), max_length=255, blank=True, null=True
    )
    copyright_license = models.CharField(
        _("copyright license"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Short name or description of the license, e.g. 'CC BY-SA 4.0'"),
    )
    copyright_license_url = models.URLField(
        _("copyright license URL"),
        max_length=200,
        blank=True,
        null=True,
        help_text=_("URL to the full text of the license"),
    )
    copyright_year = models.CharField(
        _("copyright year"), max_length=5, blank=True, null=True
    )
    credit = RichTextField(
        _("credit"),
        blank=True,
        null=True,
        help_text=_(
            "How attribution should appear on site. May include links to source. "
            "May be left blank if attribution is not required/desired. "
            "Example: Special guest post by Phil Coulson, Agent of S.H.I.E.L.D. "
        ),
    )
    provider = models.ForeignKey(
        Provider,
        verbose_name=_("provider"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    usage_terms = RichTextField(
        _("usage terms"),
        blank=True,
        null=True,
        help_text=_(
            "Textual description (for humans) describing any restrictions "
            "or terms of use. "
        ),
    )

    def __str__(self):
        return self.admin_name

    # Wagtail Admin Screen
    panels = (
        MultiFieldPanel(
            [FieldPanel("admin_name"), FieldPanel("provider"), FieldPanel("credit")]
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [FieldPanel("copyright_year"), FieldPanel("copyright_holder")]
                ),
                FieldPanel("copyright_license"),
                FieldPanel("copyright_license_url"),
                FieldPanel("usage_terms"),
            ],
            heading=_("Copyright information"),
        ),
    )


###############################################################################
# Custom Image model
###############################################################################
class AttributableImage(wagtail_images.AbstractImage):
    """
    AttributableImage adds Attribution to the base Wagtail Image model.
    """

    # Standard Wagtail Image provides `title` (alt text)
    attribution = models.ForeignKey(
        Attribution,
        verbose_name=_("attribution"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    admin_form_fields = wagtail_images.Image.admin_form_fields + ("attribution",)


class ImageRendition(wagtail_images.AbstractRendition):
    image = models.ForeignKey(
        AttributableImage, related_name="renditions", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)


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
        AttributableImage,
        verbose_name=_("attribution"),
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

    attribution = models.ForeignKey(
        Attribution,
        verbose_name=_("attribution"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    body = StreamField(
        BaseStreamBlock(),
        verbose_name=_("article body"),
        blank=True,
        help_text=_("Article text, excluding the headline (provided by 'title')"),
    )
    featured_image = models.ForeignKey(
        AttributableImage,
        verbose_name=_("attribution"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    content_panels = Page.content_panels + [
        FieldPanel("attribution"),
        StreamFieldPanel("body"),
    ]
