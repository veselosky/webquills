from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import Case, IntegerField, Q, When
from django.http.request import split_domain_port
from django.utils.translation import gettext_lazy as _

from webquills.core.models import Author


SITE_CACHE = {}
MATCH_HOSTNAME = 0
MATCH_DOMAIN = 1
MATCH_DEFAULT = 2


class SiteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("author")

    def _get_for_request(self, request):
        host = split_domain_port(request.get_host())[0]
        if host in SITE_CACHE:
            return SITE_CACHE[host]

        # Special case: if subdomain not found, select site with same root domain.
        # Handy for local dev with "localhost.domain.tld" but in prod you should
        # redirect to the main domain.
        parts = host.split(".")
        domain = ".".join(parts[-2:])
        if domain in SITE_CACHE:
            return SITE_CACHE[domain]

        sites = list(
            Site.objects.annotate(
                match=Case(
                    # annotate the results by best choice descending
                    # put exact hostname match first
                    When(domain=host, then=MATCH_HOSTNAME),
                    # then put root domain match
                    When(domain=domain, then=MATCH_DOMAIN),
                    # then match default with different hostname. there is only ever
                    # one default, so order it above (possibly multiple) hostname
                    # matches so we can use sites[0] below to access it
                    When(id=settings.SITE_ID, then=MATCH_DEFAULT),
                    # because of the filter below, if it's not default then its a hostname match
                    default=MATCH_DEFAULT,
                    output_field=IntegerField(),
                )
            )
            .filter(Q(domain__in=[host, domain]) | Q(id=settings.SITE_ID))
            .order_by("match")
        )
        if not sites:
            raise self.model.DoesNotExist()

        for site in sites:
            # Might have returned as many as 3, may as well cache them all
            SITE_CACHE[site.domain] = site
        return sites[0]

    def get_current(self, request=None):
        "Implemented for compatibility with Django sites."
        if request:
            return self._get_for_request(request)
        elif getattr(settings, "SITE_ID", ""):
            return self.get(id=settings.SITE_ID)

        raise ImproperlyConfigured(
            "You're using the Webquills sites framework without having "
            "set the SITE_ID setting. Create a site in your database and "
            "set the SITE_ID setting or pass a request to "
            "Site.objects.get_current() to fix this error."
        )

    def clear_cache(self):
        """Clear the ``Site`` object cache."""
        global SITE_CACHE
        SITE_CACHE = {}

    def get_by_natural_key(self, domain):
        return self.get(domain=domain)


class Site(models.Model):
    class Meta:
        ordering = ["domain"]
        verbose_name = _("site")
        verbose_name_plural = _("sites")

    domain = models.CharField(
        _("domain name"),
        max_length=100,
        unique=True,
    )

    name = models.CharField(_("display name"), max_length=50)

    tagline = models.CharField(
        _("tagline"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Subtitle. A few words letting visitors know what to expect."),
    )

    author = models.ForeignKey(
        Author,
        verbose_name=_("author"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Default author for any page without an explicit author"),
    )

    objects = SiteManager()

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        # Saving a site could have changed a domain, or added a new domain that
        # was previously mapped to the default site. Nuke the cache to prevent
        # old mappings overriding new ones.
        global SITE_CACHE
        super().save(*args, **kwargs)
        SITE_CACHE = {}

    def delete(self, *args, **kwargs):
        # Hopefully we don't go around deleting sites too often, but still...
        SITE_CACHE.pop(self.domain, None)
        return super().delete(*args, **kwargs)

    def natural_key(self):
        return (self.domain,)
