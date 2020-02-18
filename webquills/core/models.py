from django.db import models

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
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from webquills.core.blocks import BaseStreamBlock


@register_snippet
class FooterText(models.Model):
    """
    This provides editable text for the site footer.
    `register_snippet` allows it to be accessible via the admin. It is made
    accessible on the template via a template tag defined in navigation_tags.py
    """

    body = RichTextField()

    panels = [FieldPanel("body")]

    def __str__(self):
        return "Footer text"

    class Meta:
        verbose_name_plural = "Footer Text"


class HomePage(Page):
    """A site home page"""

    body = StreamField(BaseStreamBlock(), verbose_name="Page body", blank=True)

    content_panels = Page.content_panels + [StreamFieldPanel("body")]
