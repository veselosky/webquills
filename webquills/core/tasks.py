"""
Business logic in this app is implemented using a CQRS style. Commands should
be implemented as functions here. Queries should be implemented as methods on
Django model managers. Commands can then be called from a management command
(i.e. the CLI), a view, a signal, etc.
"""
from django.conf import settings
from django.contrib.sites.models import Site

from webquills.core.models import SiteMeta, HomePage, Status


def initialize_site():
    """
    For development environments, set up the Site and home page objects.
    """
    try:
        site = Site.objects.get(id=settings.SITE_ID)
        # If the default site was already created, just update its properties
        site.domain = "webquills.com"
        site.name = "WebQuills"
    except Site.DoesNotExist:
        site = Site.objects.create(
            id=settings.SITE_ID,
            domain="webquills.com",
            name="WebQuills",
        )
    if not hasattr(site, "meta"):
        SiteMeta.objects.create(
            site=site, name="WebQuills", tagline="Tips, Tools, & Tech for Writers"
        )
    site.save()
    site.refresh_from_db()

    try:
        hp = HomePage.objects.get(id=1)
    except HomePage.DoesNotExist:
        hp = HomePage.objects.create(
            headline=site.name,
            slug="default-home-page",
            status=Status.USABLE,
        )