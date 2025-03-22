from __future__ import annotations

import idna
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import Case, IntegerField, Value, When
from django.http.request import split_domain_port
from django.utils.functional import cached_property

User = get_user_model()


def normalize_domain(domain: str) -> str:
    """Normalize a domain name according to RFC 3986 and RFC 3987."""
    domain = domain.strip().lower().rstrip(".")  # Remove trailing dots and lowercase
    domain = idna.encode(domain).decode("ascii")  # Convert to Punycode if needed
    return domain


def get_domain_variants(domain: str) -> list[str]:
    """Return a list of domain variants to check for in the database.

    Variants include the normalized domain with and without the port number.
    """
    domain, port = split_domain_port(domain)
    host = normalize_domain(domain)
    domain_variants = [host]
    if port:
        domain_variants.append(f"{host}:{port}")
    return domain_variants


#######################################################################################
# Block Reason Model
#######################################################################################
class BlockReason(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

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
        return (
            self.filter(group__in=user.groups.all())
            .values_list("id", flat=True)
            .distinct()
        )


class SiteManager(models.Manager):
    def get_queryset(self):
        return (
            super().get_queryset().select_related("owner").prefetch_related("domains")
        )

    def get_for_request(self, request) -> Site:
        """
        Retrieve the Site object for the given request.

        - Uses `request.get_host()` to get the domain and port.
        - Checks for both `domain:port` and domain-only matches in a single query.
        - Explicitly prioritizes an exact match on `domain:port` using database ordering.
        - Performs a case-insensitive lookup.
        """
        # Construct possible domain matches
        domain_variants = get_domain_variants(request.get_host())
        # Annotate results to prioritize exact domain:port matches
        sites = (
            self.get_queryset()
            .filter(domains__normalized_domain__exact__in=domain_variants)
            .annotate(
                priority=Case(
                    When(domains__domain__exact=domain_variants[0], then=Value(0)),
                    When(domains__domain__exact=domain_variants[1], then=Value(1)),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            )
            .order_by("priority")
            .distinct()
        )

        return sites.first()


class Site(models.Model):
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="sites")
    group = models.OneToOneField(
        "auth.Group", on_delete=models.PROTECT, related_name="site"
    )
    name = models.CharField(max_length=255)
    create_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    archive_date = models.DateTimeField(null=True, blank=True)
    archived_canonical_name = models.CharField(max_length=255, blank=True)
    block_reason = models.ForeignKey(
        BlockReason, on_delete=models.SET_NULL, null=True, blank=True
    )

    # domains = related_name from Domain FK

    objects = SiteManager.from_queryset(SiteQuerySet)()

    @cached_property
    def canonical_domain(self) -> Domain:
        return self.domains.filter(is_canonical=True).first()

    @cached_property
    def primary_domain(self) -> Domain:
        return self.domains.filter(is_primary=True).first()

    @property
    def domain(self) -> str:
        """For compatibility with Django's RequestSite (returns primary domain string)"""
        if self.primary_domain:
            return self.primary_domain.display_domain
        return ""

    def __str__(self) -> str:
        return f"{self.name} ({self.domain or 'No Primary Domain'})"


#######################################################################################
# Domain Model and support classes
#######################################################################################
class DomainManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("site")

    def get_for_request(self, request) -> Domain:
        """
        Returns the Domain object best matching the given request.

        - Uses `request.get_host()` to get the domain and port.
        - Performs domain name normalization before lookup.
        """
        # Construct possible domain matches
        domain_variants = get_domain_variants(request.get_host())
        # Annotate results to prioritize exact domain:port matches
        domains = (
            self.get_queryset()
            .filter(normalized_domain__exact__in=domain_variants)
            .annotate(
                priority=Case(
                    When(domain__exact=domain_variants[0], then=Value(0)),
                    When(domain__exact=domain_variants[1], then=Value(1)),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            )
            .order_by("priority")
            .distinct()
        )
        return domains.first()


class Domain(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="domains")
    display_domain = models.CharField(max_length=255, unique=True)
    normalized_domain = models.CharField(max_length=255, unique=True)

    is_primary = models.BooleanField(default=False)
    is_canonical = models.BooleanField(default=False)

    class Meta:
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

    def __str__(self) -> str:
        status = []
        if self.is_primary:
            status.append("Primary")
        if self.is_canonical:
            status.append("Canonical")
        return f"{self.display_domain} ({', '.join(status) if status else 'Alternate'})"
