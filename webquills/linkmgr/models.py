from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db import models
from django.utils.translation import gettext_lazy as _


class LinkCategory(models.Model):
    class Meta:
        unique_together = ("site", "slug")
        verbose_name = _("link list")
        verbose_name_plural = _("link lists")

    name = models.CharField(_("name"), max_length=50, blank=False, null=False)
    slug = models.SlugField(_("slug"))
    site = models.ForeignKey(
        "sites.Site",
        verbose_name=_("site"),
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="link_lists",
    )

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        key = make_template_fragment_key("category_links", [self.site_id, self.slug])
        cache.delete(key)


class Link(models.Model):
    class Meta:
        order_with_respect_to = "category"
        verbose_name = _("link")
        verbose_name_plural = _("links")

    url = models.CharField(_("URL"), max_length=255, blank=False, null=False)
    text = models.CharField(_("text"), max_length=50, blank=False, null=False)
    icon = models.CharField(
        _("icon"),
        max_length=50,
        blank=False,
        null=False,
        default="link-45deg",
        help_text="<a href=https://icons.getbootstrap.com/#icons target=iconlist>icon list</a>",
    )
    category = models.ForeignKey(
        LinkCategory,
        verbose_name=_("list"),
        on_delete=models.CASCADE,
        related_name="links",
    )

    def __str__(self) -> str:
        return f"{self.text}({self.url})"
