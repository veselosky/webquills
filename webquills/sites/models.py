from __future__ import annotations

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.http.request import split_domain_port
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from webquills.sites.validators import normalize_domain, validate_subdomain
from webquills.themes import get_theme_choices

User = get_user_model()


#######################################################################################
# Block Reason Model
#######################################################################################
class BlockReason(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        # Translators: Means "the reason a site is blocked".
        verbose_name = _("block reason")
        verbose_name_plural = _("block reasons")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        return super().save(*args, **kwargs)


#######################################################################################
# Site Model and support classes
#######################################################################################
class SiteQuerySet(models.QuerySet):
    def ids_for_user(self, user) -> list[int]:
        """Return a list of site IDs that the given user has access to.

        Use this when you need to filter a queryset of sites based on user permissions,
        but do not otherwise need to instantiate the Site objects.
        """
        # A user may have access to sites they do not own. Access permission is
        # determined by group membership.
        return list(
            self.filter(group__in=user.groups.all())
            .values_list("id", flat=True)
            .distinct()
        )

    def for_user(self, user) -> SiteQuerySet:
        """Return a queryset of sites that the given user has access to.

        Use this when you need to filter a queryset of sites based on user permissions,
        and you do need to instantiate the Site objects.
        """
        # A user may have access to sites they do not own. Access permission is
        # determined by group membership.
        return self.filter(group__in=user.groups.all())


class SiteManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("owner", "group")
            .prefetch_related("domains")
        )

    def get_for_request(self, request) -> Site | None:
        """
        Returns the Site object best matching the given request.

        Uses `Domain.get_for_request` to find the Domain, then returns the associated
        Site.
        """
        domain = Domain.objects.get_for_request(request)
        if domain:
            return domain.site
        return None


class Site(models.Model):
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="sites")
    group = models.OneToOneField(
        "auth.Group", on_delete=models.PROTECT, related_name="site"
    )
    name = models.CharField(max_length=255)
    # Length is constrained by RFC1035 to 63 characters
    subdomain = models.CharField(
        _("subdomain"),
        max_length=64,
        unique=True,
        help_text=_("Subdomain for the site"),
        validators=[validate_subdomain],
    )
    # Normalized domains may have more characters than the display domain, but still
    # must fit in 64 characters.
    normalized_subdomain = models.SlugField(
        _("normalized subdomain"),
        max_length=64,
        unique=True,
        help_text=_("Normalized subdomain for the site"),
    )
    create_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    archive_date = models.DateTimeField(null=True, blank=True)
    archived_canonical_name = models.CharField(max_length=255, blank=True)
    block_reason = models.ForeignKey(
        BlockReason, on_delete=models.SET_NULL, null=True, blank=True
    )
    theme_app = models.CharField(
        max_length=255,
        choices=get_theme_choices,
        default="cleanblog",
        help_text=_("Choose a theme for the site"),
    )

    # domains = related_name from Domain FK

    objects = SiteManager.from_queryset(SiteQuerySet)()

    class Meta:
        verbose_name = _("site")
        verbose_name_plural = _("sites")
        ordering = ["subdomain"]

    def __str__(self) -> str:
        return f"{self.name} ({self.domain or 'No Primary Domain'})"

    def get_absolute_url(self):
        return reverse("site_update", kwargs={"pk": self.pk})

    @cached_property
    def canonical_domain(self) -> Domain:
        return self.domains.filter(is_canonical=True).first()

    @cached_property
    def primary_domain(self) -> Domain:
        return self.domains.filter(is_primary=True).first()

    @cached_property
    def theme(self) -> str:
        """
        Returns the theme instance for the site.
        """
        theme_app = apps.get_app_config(self.theme_app)
        return theme_app.get_theme_for_site(self)

    @property
    def domain(self) -> str:
        """For compatibility with Django's RequestSite (returns primary domain string)"""
        if self.primary_domain:
            return self.primary_domain.display_domain
        return ""

    @classmethod
    def get_for_request(cls, request) -> Site | None:
        """
        Shortcut method for Site.objects.get_for_request(request).
        """
        return cls.objects.get_for_request(request)


#######################################################################################
# Domain Model and support classes
#######################################################################################
class DomainManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("site")

    def get_for_request(self, request) -> Domain | None:
        """
        Returns the Domain object best matching the given request.

        - Uses `request.get_host()` to get the domain and port.
        - Performs domain name normalization before lookup.

        If the domain is not found, returns None.
        """
        host, port = split_domain_port(request.get_host())
        domain = normalize_domain(host)
        # We don't want to return a Domain for sites that are archived or blocked.
        return (
            self.get_queryset()
            .filter(
                normalized_domain=domain,
                site__archive_date=None,
                site__block_reason=None,
            )
            .first()
        )


class Domain(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="domains")
    display_domain = models.CharField(max_length=255, unique=True)
    normalized_domain = models.CharField(max_length=255, unique=True)

    is_primary = models.BooleanField(default=False)
    is_canonical = models.BooleanField(default=False)

    objects = DomainManager()

    class Meta:
        verbose_name = _("domain")
        verbose_name_plural = _("domains")
        ordering = ["site", "normalized_domain"]
        constraints = [
            models.UniqueConstraint(
                fields=["site"],
                condition=models.Q(is_primary=True),
                name="unique_primary_domain",
            ),
            models.UniqueConstraint(
                fields=["site"],
                condition=models.Q(is_canonical=True),
                name="unique_canonical_domain",
            ),
        ]
        indexes = [
            models.Index(fields=["site"]),
            models.Index(fields=["normalized_domain"]),
            models.Index(fields=["is_primary"]),
            models.Index(fields=["is_canonical"]),
        ]

    def __str__(self) -> str:
        status = []
        if self.is_primary:
            status.append("Primary")
        if self.is_canonical:
            status.append("Canonical")
        return f"{self.display_domain} ({', '.join(status) if status else 'Alternate'})"

    def save(self, *args, **kwargs):
        """
        Ensure that at most one domain per site is marked as primary and canonical,
        within a single atomic transaction.
        """
        self.normalized_domain = normalize_domain(self.display_domain)
        with transaction.atomic():
            if self.is_primary:
                qs = Domain.objects.filter(site=self.site, is_primary=True)
                if self.pk:
                    qs = qs.exclude(pk=self.pk)
                qs.update(is_primary=False)
            if self.is_canonical:
                qs = Domain.objects.filter(site=self.site, is_canonical=True)
                if self.pk:
                    qs = qs.exclude(pk=self.pk)
                qs.update(is_canonical=False)

            super().save(*args, **kwargs)
