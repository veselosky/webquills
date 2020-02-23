import wagtail.images.models as wagtail_images
from django.db import models
from django.utils.translation import gettext_lazy as _
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

from webquills.core.apps import default_richtext_features
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

    body = RichTextField(features=default_richtext_features, blank=True, null=True)

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

    # Attribution Fields
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
        features=default_richtext_features,
        help_text=_(
            "How attribution should appear on site. May include links to source. "
            "May be left blank if attribution is not required/desired. "
            "Example: Special guest post by Phil Colson, Agent of S.H.I.E.L.D. "
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
        features=default_richtext_features,
        help_text=_(
            "Textual description (for humans) describing any restrictions "
            "or terms of use. "
        ),
    )

    # Attribution Metadata
    def __str__(self):
        return self.admin_name

    class Meta:
        verbose_name = _("attribution")
        verbose_name_plural = _("attributions")

    # Attribution Admin Screen
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
    """A site home page"""

    body = StreamField(BaseStreamBlock(), verbose_name="Page body", blank=True)

    content_panels = Page.content_panels + [StreamFieldPanel("body")]
