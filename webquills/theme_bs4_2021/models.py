"""
A Theme is a collection of attributes:
- base stylesheet (original bootstrap or a bootswatch variant)
- custom stylesheet (local file, customization layer)
- navigation menu: A list of links. Use linkmgr.
- sidebar definition: List of modules (Includes)
- footer definition: same as sidebar

A saved Theme is site-specific, but there is also a generic default Theme that
is used by default when there are no custom Themes or a site has no Theme
assigned. A site can have any number of Themes associated with it, but only
one is active at a time.
"""
from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from webquills.core.models import CategoryPage
from webquills.sites.models import Site


conf = apps.get_app_config("bs4theme")


class ModuleList(models.Model):
    """
    A ModuleList is a labeled container for ThemeModules.
    """

    class Meta:
        verbose_name = _("modulelist")
        verbose_name_plural = _("modulelists")

    name = models.CharField(
        _("name"),
        max_length=255,
        help_text=_("A name for the admin, not visible to the public"),
    )
    slug = models.SlugField(_("slug"))
    headline = models.TextField(
        verbose_name=_("headline"),
        blank=True,
        null=False,
        default="",
        max_length=255,
        help_text=_("A title for the list, visible on the public web site"),
    )
    # thememodule_set = ThemeModule.reverseFK

    def __getitem__(self, index):
        the_set = self.thememodule_set.all()[index]
        if isinstance(the_set, ThemeModule):
            # index was an int
            return the_set.module
        # index was a slice, the_set will be iterable
        return [tm.module for tm in the_set]

    def __iter__(self):
        for tm in self.thememodule_set.all():
            yield tm.module

    def __len__(self):
        return self.thememodule_set.all().count()

    def __str__(self):
        return self.name


class ThemeModule(models.Model):
    """
    A ThemeModule is a block that can be included in various spots in the page.
    It is an abstraction over any "includable" model, where includable means it
    has these methods: partial_template, get_partial_url. A
    ThemeModule belongs to a ModuleList.
    """

    class Meta:
        verbose_name = _("theme module")
        verbose_name_plural = _("theme modules")
        order_with_respect_to = "module_list"

    module_list = models.ForeignKey(
        ModuleList,
        verbose_name=_("list"),
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    content_type = models.ForeignKey(
        "contenttypes.ContentType",
        verbose_name=_("content type"),
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    module = GenericForeignKey("content_type", "object_id")


class Theme(models.Model):
    """
    A Theme is a collection of site-specific design decisions.
    """

    class Meta:
        verbose_name = _("theme")
        verbose_name_plural = _("themes")

    name = models.CharField(
        verbose_name=_("name"),
        unique=True,
        max_length=255,
        help_text=_("A unique name for the admin, not visible to public"),
    )
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    is_active = models.BooleanField(
        verbose_name=_("is active"),
        default=False,
    )
    base_stylesheet = models.CharField(
        _("base stylesheet"),
        max_length=255,
        null=False,
        blank=False,
        default=conf.bootstrap_themes[0]["cssCdn"],
        choices=conf.style_choices,
    )

    custom_stylesheet = models.FilePathField(
        path=str(settings.STATIC_ROOT),
        recursive=True,
        match=r".*\.css$",
        verbose_name=_("custom stylesheet"),
        max_length=255,
        blank=True,
        null=False,
        default="",
    )

    custom_nav_menu = models.ForeignKey(
        "linkmgr.LinkCategory",
        verbose_name=_("navigation menu"),
        on_delete=models.SET_NULL,
        # No reverse method, might have multiple FKs in future
        related_name="+",
        blank=True,
        null=True,
    )

    custom_sidebar = models.ForeignKey(
        ModuleList,
        verbose_name=_("custom sidebar"),
        on_delete=models.SET_NULL,
        # No reverse method, multiple FKs make it confusing
        related_name="+",
        blank=True,
        null=True,
    )

    custom_footer = models.ForeignKey(
        ModuleList,
        verbose_name=_("custom footer"),
        on_delete=models.SET_NULL,
        # No reverse method, multiple FKs make it confusing
        related_name="+",
        blank=True,
        null=True,
    )

    @property
    def nav_menu(self):
        """
        Returns an interable of objects having a `headline` property and a
        `get_absolute_url` method.
        """
        if self.custom_nav_menu:
            return self.custom_nav_menu
        # If no custom menu, default to category pages
        return (
            CategoryPage.objects.live()
            .filter(site=self.site, menu_order__gt=0)
            .order_by("menu_order")
        )

    @property
    def sidebar_modules(self):
        return self.custom_sidebar or []

    @property
    def footer_modules(self):
        return self.custom_footer or []

    def __str__(self):
        return self.name
