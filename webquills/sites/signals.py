from django.contrib.sites.models import Site as DjangoSite
from django.db.models.signals import post_save

from webquills.core.models import Author
from .models import SITE_CACHE, Site


def clear_site_cache_for_author(sender, **kwargs):
    if kwargs["created"] or kwargs["raw"]:
        # New data loading, won't be in cache
        return

    instance, using = kwargs["instance"], kwargs["using"]
    # get a list of the domains that use this author as their default
    domains = (
        Site.objects.using(using)
        .filter(author=instance)
        .only("domain")
        .values_list("domain", flat=True)
    )
    for domain in domains:
        SITE_CACHE.pop(domain)


def ensure_wqsite_for_django_site(sender, **kwargs):
    if kwargs["created"]:
        Site.objects.get_or_create(site_ptr=kwargs["instance"])


def connect_signals():
    post_save.connect(
        clear_site_cache_for_author,
        sender=Author,
        dispatch_uid="clear_site_cache_for_author",
    )

    post_save.connect(
        ensure_wqsite_for_django_site,
        sender=DjangoSite,
        dispatch_uid="ensure_wqsite_for_django_site",
    )
