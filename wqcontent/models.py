"""
Webquills core content models.
"""

import mimetypes
import typing as T

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.translation import to_locale
from django.utils.html import format_html
from django.utils import timezone
from taggit.managers import TaggableManager

from wqlinklist.models import LinkList

# Transform "en-us" to "en_US"
DEFAULT_LOCALE = to_locale(settings.LANGUAGE_CODE)


######################################################################################
# Site Vars
######################################################################################
class SiteVarQueryset(models.QuerySet):
    def get_value(self, name: str, default: str = "", asa: T.Callable = str):
        """
        Given a queryset pre-filtered by site, returns the value of the SiteVar with
        the given name. If no value is set for that name, returns the passed default
        value, or empty string if no default was passed. To transform the stored string
        to another type, pass a transform function in the asa argument. The default
        value should be passed as a string; it will be passed to the asa function
        for transformation.

        Examples:

        # Returns the string if set, or "" if not set
        x = site.vars.get_value("analytics_id")
        # Returns the string if set, or "Ignore" if not set
        x = site.vars.get_value("abort_retry_ignore", "Ignore")
        # Returns the number of pages as an integer. Note the default should be a str.
        num_items = site.vars.get_value("paginate_by", default="10", asa=int)
        # Parses the value as JSON and returns the result
        data = site.vars.get_value("json_data", "{}", json.loads)
        """
        try:
            return asa(self.get(name=name).value)
        except self.model.DoesNotExist:
            # Anything that can be a site var can also be configured app-wide.
            conf = apps.get_app_config("wqcontent")
            if hasattr(conf, name):
                return asa(getattr(conf, name))
            # This allows None as a default, without crashing on e.g. `int(None)`
            return asa(default) if default is not None else default
        # Note explicitly NOT catching MultipleObjectsReturned, that's still an error


class SiteVar(models.Model):
    """
    Site-specific variables are stored here. All site variable are injected into
    template contexts using the site context processor in
    ``wqcontent.apps.context_defaults``. You can store any variables for your own
    site.
    """

    class Meta:
        base_manager_name = "objects"
        unique_together = ("site", "name")
        verbose_name = _("site variable")
        verbose_name_plural = _("site variables")

    site = models.ForeignKey(
        "sites.Site",
        verbose_name=_("site"),
        on_delete=models.CASCADE,
        related_name="vars",
    )
    name = models.CharField(_("name"), max_length=100)
    value = models.TextField(_("value"))

    objects = SiteVarQueryset.as_manager()

    def __str__(self):
        return f"{self.name}={self.value} ({self.site.domain})"


class Author(models.Model):
    """
    Author is a container for attribution and copyright information, not necessarily
    representing an actual person, but a pen name or persona.
    """

    class Meta:
        verbose_name = _("author")
        verbose_name_plural = _("authors")
        constraints = [
            models.UniqueConstraint(
                fields=["site", "name"], name="unique_author_name_per_site"
            )
        ]

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    name = models.CharField(
        _("name"),
        max_length=255,
        blank=True,
        help_text=_(
            "As in a newspaper byline, a name to attribute authorship of an article, "
            "e.g. 'Edward R. Murrow' (omit the word 'by')."
        ),
    )
    description = models.TextField(
        verbose_name=_("about"),
        blank=True,
        help_text=_(
            "A paragraph or two about the author. May include a headshot, links to "
            "the author's website, recent publications, etc. Typically displayed in "
            "article footer or sidebar. "
        ),
    )
    biography = models.TextField(
        verbose_name=_("biography"),
        blank=True,
        help_text=_(
            "A longer biography of the author, suitable for a dedicated 'About the "
            "Author' page. "
        ),
    )
    social_links = models.ForeignKey(
        LinkList,
        verbose_name=_("social links"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_(
            "A list of links to the author's websites and/or social media profiles."
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
    copyright_notice = models.TextField(
        verbose_name=_("copyright notice"),
        blank=True,
        help_text=_("A custom copyright notice to replace the default. "),
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.copyright_holder})"


######################################################################################
# Base Classes
######################################################################################


######################################################################################
# This vocabulary taken from IPTC standards, upon which https://schema.org/CreativeWork
# is based.
class Status(models.TextChoices):
    WITHHELD = "withheld", _("Draft (withheld)")
    USABLE = "usable", _("Publish (usable)")
    CANCELLED = "cancelled", _("Unpublish (cancelled)")


######################################################################################
class CreativeWork(models.Model):
    """
    <https://schema.org/CreativeWork>. CreativeWork is the base class for all content.

    CreativeWork houses the common properties of content described by Schema.org, including
    copyright information and publication status, as well as some properties used for
    internal management.

    Every CreativeWork has foreign keys to site (Site) and owner (User). The owner is
    nullable for convenience of programatically created content, but is required for
    content created by users. The site is required for all content, and is used to
    determine the permissions, site-specific settings, and appearance of the content.

    Additionally, every CreativeWork is expected to be able to produce a schema.org
    dictionary for use in JSON-LD serialization, and a list of open graph properties
    and values describing itself. This is done by overriding the `schema_dict` and
    `opengraph` properties in subclasses. Opengraph data is returned as a list of
    key-value pairs rather than a dictionary because open graph allows duplicate keys,
    and the order of the keys is significant.
    """

    # Database properties
    class Meta:
        abstract = True
        get_latest_by = "date_published"
        # Nearly all queries will filter on these fields
        indexes = [models.Index(fields=["site", "status", "date_published", "expires"])]

    # As Things, CreativeWorks have a name (or title) and description. For most
    # subclasses, title is required.
    title = models.CharField(_("title"), max_length=255)
    description = models.CharField(
        _("description"),
        max_length=255,
        blank=True,
        help_text=_("A short summary of the item. Plain text only, no markup allowed."),
    )
    site = models.ForeignKey(
        Site,
        verbose_name=_("site"),
        on_delete=models.CASCADE,
        default=1,
        related_name="+",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="+",
        help_text=_(
            "The user who created/uploaded the content (for internal permissions, audits)."
        ),
    )
    author = models.ForeignKey(
        Author,
        verbose_name=_("author"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
    )
    # From https://schema.org/creativeWorkStatus
    status = models.CharField(
        _("status"),
        max_length=50,
        choices=Status.choices,
        default=Status.USABLE,
        help_text=_(
            'Must be "usable" to appear on the site. '
            'See <a href="https://schema.org/creativeWorkStatus">Schema.org</a> '
            "for details."
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
    custom_copyright_notice = models.TextField(
        verbose_name=_("copyright notice"),
        blank=True,
        help_text=_("A custom copyright notice to replace the default. "),
    )
    date_created = models.DateTimeField(_("date created"))
    date_modified = models.DateTimeField(_("date modified"), auto_now=True)
    date_published = models.DateTimeField(_("date published"), blank=True, null=True)
    expires = models.DateTimeField(
        _("expires"),
        blank=True,
        null=True,
        help_text=_("The date and time at which the page will no longer be available."),
    )

    tags = TaggableManager(blank=True)

    # Class properties
    icon_name = "file"
    schema_type = "CreativeWork"

    # Calculated properties
    @property
    def copyright_holder(self):
        if self.custom_copyright_holder:
            return self.custom_copyright_holder
        if self.author and self.author.copyright_holder:
            return self.author.copyright_holder
        return self.site.vars.get_value("copyright_holder", default=self.site.name)

    @property
    def copyright_notice(self):
        if self.custom_copyright_notice:
            return self.custom_copyright_notice.format(self.copyright_year)
        elif self.author and self.author.copyright_notice:
            return self.author.copyright_notice.format(self.copyright_year)
        elif self.site.vars.get_value("copyright_notice"):
            return self.site.vars.get_value("copyright_notice").format(
                self.copyright_year
            )
        config = apps.get_app_config("wqcontent")
        tpl = config.fallback_copyright
        notice = tpl.format(self.copyright_year, self.copyright_holder)
        return notice

    @property
    def copyright_year(self):
        "Subclasses should implement their own copyright year"
        return self.date_published.year

    @property
    def schema_dict(self):
        return {
            "@context": "https://schema.org",
            "@type": self.schema_type,
            "datePublished": self.date_published.isoformat()
            if self.date_published
            else None,
            "author": self.author.name if self.author else None,
            "publisher": self.site.name,
            "copyrightHolder": self.copyright_holder,
            "copyrightYear": self.copyright_year,
        }

    @property
    def opengraph(self):
        # The opengraph properties for media objects look very different from the
        # ones for pages, so there's no sensible default to place here.
        raise NotImplementedError("Subclasses must implement opengraph property")

    def __str__(self):
        return f"{self.title} ({self.site.name})"

    def save(self, *args, **kwargs):
        # We don't use auto_now_add because that would override a manually provided value,
        # but we still want to set a default.
        if not self.date_created:
            self.date_created = timezone.now()
        return super().save(*args, **kwargs)


######################################################################################
# Media Objects
######################################################################################
class MediaObject(CreativeWork):
    """Abstract base class for stored media files (image, audio, video, attachment).

    Every media object has an `content_field` attribute that names the field containing
    its content. This field is a FileField or ImageField, and is used to store the media
    file itself. The `content_field` is required to be overridden in subclasses.

    If `mime_type` is not populated, it will be guessed when the instance is saved,
    based on the file name stored in the `content_field` (using `mimetypes.guess_type`).
    """

    # Database properties
    class Meta(CreativeWork.Meta):
        abstract = True

    # For MediaObjects, title is optional to facilitate easy uploads.
    title = models.CharField(
        _("title"), max_length=255, blank=True, help_text=_("Optional title")
    )
    # Open Graph has `type`, Schema.org calls it `encodingFormat`, both recommend MIME
    # type as the value
    mime_type = models.CharField(
        _("MIME type"), max_length=255, db_index=True, blank=True
    )
    upload_date = models.DateTimeField(_("when uploaded"), auto_now_add=True)

    # Class properties
    content_field = None  # Must override in subclasses
    icon_name = "file-richtext"
    schema_type = "MediaObject"

    @property
    def _base_url(self):
        protocol = "http" if settings.DEBUG else "https"
        return f"{protocol}://{self.site.domain}"

    @property
    def url(self):
        path = getattr(self, self.content_field).url
        return f"{self._base_url}{path}"

    def save(self, *args, **kwargs):
        content_file = getattr(self, self.content_field)
        if content_file and not self.mime_type:
            self.mime_type, _ = mimetypes.guess_type(content_file.name, strict=False)
        return super().save(*args, **kwargs)


######################################################################################
class Image(MediaObject):
    class Meta(MediaObject.Meta):
        verbose_name = _("image")
        verbose_name_plural = _("images")

    image_file = models.ImageField(
        _("image file"),
        width_field="width",
        height_field="height",
        max_length=255,
    )
    width = models.IntegerField(_("width"), blank=True)
    height = models.IntegerField(_("height"), blank=True)
    alt_text = models.CharField(verbose_name=_("alt text"), max_length=255, blank=True)

    # Class properties
    content_field = "image_file"
    icon_name = "image"
    schema_type = "ImageObject"

    @property
    def schema_dict(self):
        schema = super().schema_dict
        schema["@type"] = self.schema_type
        schema["contentUrl"] = self.url
        schema["width"] = self.width
        schema["height"] = self.height
        return schema

    @property
    def opengraph(self):
        return [
            ("og:image", self.url),
            ("og:image:width", self.width),
            ("og:image:height", self.height),
            ("og:image:alt", self.alt_text),
        ]


######################################################################################
class Attachment(MediaObject):
    class Meta(MediaObject.Meta):
        verbose_name = _("attachment")
        verbose_name_plural = _("attachments")

    content_field = "file"
    icon_name = "file"

    file = models.FileField(_("file"), max_length=255)


######################################################################################
# Web Pages
######################################################################################


######################################################################################
class BasePage(CreativeWork):
    """
    Abstract base class for all web pages.
    """

    class Meta(CreativeWork.Meta):
        abstract = True
        get_latest_by = "date_published"
        ordering = ["-date_published"]

    # Database properties
    slug = models.SlugField(_("slug"), max_length=255)
    body = models.TextField(
        _("body"), blank=True, help_text=_("Main content of the page")
    )
    share_image = models.ForeignKey(
        "Image",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Image for social sharing"),
        related_name="+",
    )
    base_template = models.CharField(
        _("base template"),
        max_length=255,
        blank=True,
        help_text=_(
            "Replaces the standard base.html root layout. This allows you to have a "
            "totally custom layout for a page."
        ),
    )
    content_template = models.CharField(
        _("content body template"),
        max_length=255,
        blank=True,
        help_text=_(
            "The template that renders the content body within the page layout "
            "provided by the base.html. This only affects the 'main' section of "
            "the page, the rest of the layout is inherited from base.html."
        ),
    )
    seo_title = models.CharField(_("SEO title override"), max_length=255, blank=True)
    seo_description = models.CharField(
        _("SEO description override"), max_length=255, blank=True
    )
    custom_icon = models.CharField(
        _("custom icon"),
        max_length=255,
        blank=True,
        help_text=_(
            "Name of an icon to represent the page. <a href=https://icons.getbootstrap.com/#icons target=iconlist>icon list</a>"
        ),
    )

    # Class properties
    schema_type = "WebPage"
    opengraph_type = "website"

    @property
    def icon_name(self):
        "name of an icon to represent this object"
        return self.custom_icon or self.site.vars.get_value("default_icon", "file-text")

    @property
    def url(self):
        return self.get_absolute_url()

    @property
    def excerpt(self):
        """Rich text excerpt for use in teases and feed content. If no excerpt has
        been specified, returns the full body text."""
        config = apps.get_app_config("wqcontent")
        if not self.body:
            return ""
        excerpt = self.body.split(config.pagebreak_separator, maxsplit=1)[0]
        return excerpt

    @property
    def has_excerpt(self):
        """True if there is more body text to read after the excerpt. False if
        excerpt == body.
        """
        config = apps.get_app_config("wqcontent")
        return config.pagebreak_separator in self.body

    @property
    def opengraph(self):
        og = [
            ("og:type", self.opengraph_type),
            ("og:title", self.title),
            ("og:description", self.description),
            ("og:url", self.url),
            ("og:site_name", self.site.name),
            ("og:locale", DEFAULT_LOCALE),
        ]
        if self.share_image:
            og.extend(self.share_image.opengraph)
        return og


######################################################################################
class CreativeWorkQuerySet(models.QuerySet):
    def live(self):
        return self.filter(
            models.Q(expires__isnull=True) | models.Q(expires__gt=timezone.now()),
            status=Status.USABLE,
            date_published__lte=timezone.now(),
        )


######################################################################################
class PageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("site", "share_image")


#######################################################################
class Page(BasePage):
    "A model to represent a generic evergreen page or 'landing page'."

    class Meta(BasePage.Meta):
        verbose_name = _("page")
        verbose_name_plural = _("pages")
        constraints = [
            models.UniqueConstraint(
                fields=["site", "slug"], name="page_unique_slug_per_site"
            )
        ]

    objects = PageManager.from_queryset(CreativeWorkQuerySet)()

    # Class properties
    @property
    def opengraph(self):
        return [
            ("og:type", self.opengraph_type),
            ("og:title", self.title),
            ("og:description", self.description),
            ("og:url", self.url),
            ("og:site_name", self.site.name),
            ("og:locale", DEFAULT_LOCALE),
        ]

    def get_absolute_url(self):
        return reverse("landing_page", kwargs={"page_slug": self.slug})


#######################################################################
class Section(BasePage):
    "A model to represent major site categories."

    class Meta(BasePage.Meta):
        verbose_name = _("section")
        verbose_name_plural = _("sections")
        constraints = [
            models.UniqueConstraint(
                fields=["site", "slug"], name="section_unique_slug_per_site"
            )
        ]

    objects = PageManager.from_queryset(CreativeWorkQuerySet)()

    def get_absolute_url(self):
        return reverse("section_page", kwargs={"section_slug": self.slug})


#######################################################################
class HomePage(BasePage):
    "A model to represent the site home page."

    class Meta(BasePage.Meta):
        verbose_name = _("home page")
        verbose_name_plural = _("home pages")

    admin_name = models.CharField(
        _("admin name"),
        max_length=255,
        help_text=_("Name used in the admin to distinguish from other home pages"),
    )
    objects = PageManager.from_queryset(CreativeWorkQuerySet)()

    def get_absolute_url(self):
        return reverse("home_page")


#######################################################################
class ArticleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("site", "section", "share_image")


#######################################################################
class Article(BasePage):
    "Articles are the bread and butter of a site. They will appear in feeds."

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["site", "section", "slug"],
                name="article_unique_slug_per_section",
            )
        ]
        ordering = ["-date_published"]
        verbose_name = _("article")
        verbose_name_plural = _("articles")

    section = models.ForeignKey(
        Section, verbose_name=_("section"), on_delete=models.PROTECT
    )
    image_set = models.ManyToManyField(Image, verbose_name=_("related images"))
    attachment_set = models.ManyToManyField(Attachment, verbose_name=_("attachments"))

    objects = ArticleManager.from_queryset(CreativeWorkQuerySet)()

    # Class properties
    schema_type = "Article"
    opengraph_type = "article"

    @property
    def opengraph(self):
        og = super().opengraph
        og.append(("article:published_time", self.date_published.isoformat()))
        og.append(("article:modified_time", self.date_modified.isoformat()))
        if self.expires:
            og.append(("article:expiration_time", self.expires.isoformat()))
        og.append(("article:section", self.section.title))
        # FIXME Author should be the URL of a profile page, not just the name
        if self.author:
            og.append(("article:author", self.author.name))
        return og

    def get_absolute_url(self):
        return reverse(
            "article_page",
            kwargs={"article_slug": self.slug, "section_slug": self.section.slug},
        )


######################################################################################
class SectionMenu:
    def __init__(self, site: Site, title: str = "", sections=None, pages=None) -> None:
        self.site = site
        self.title = title
        self.sections = sections or Section.objects.live().filter(site=site).order_by(
            "title"
        )
        self.pages = pages

    @property
    def links(self):
        home = HomePage.objects.live().filter(site=self.site).latest()
        menu = [home]
        menu.extend(self.sections)
        if self.pages:
            menu.extend(self.pages)
        return menu
