from django.apps import apps as global_apps
from django.conf import settings
from django.core.management.color import no_style
from django.db import DEFAULT_DB_ALIAS, connections, router
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


def create_default_site(
    app_config,
    verbosity=2,
    interactive=True,
    using=DEFAULT_DB_ALIAS,
    apps=global_apps,
    **kwargs
):
    """
    Creates the default Site object. Cribbed verbatim from Django 3.2.
    """
    try:
        Site = apps.get_model("sites", "Site")
    except LookupError:
        return

    if not router.allow_migrate_model(using, Site):
        return

    if not Site.objects.using(using).exists():
        # The default settings set SITE_ID = 1, and some tests in Django's test
        # suite rely on this value. However, if database sequences are reused
        # (e.g. in the test suite after flush/syncdb), it isn't guaranteed that
        # the next id will be 1, so we coerce it. See #15573 and #16353. This
        # can also crop up outside of tests - see #15346.
        if verbosity >= 2:
            print("Creating webquills.com Site object")
        Site(
            pk=getattr(settings, "SITE_ID", 1),
            domain="webquills.com",
            name="webquills.com",
        ).save(using=using)

        # We set an explicit pk instead of relying on auto-incrementation,
        # so we need to reset the database sequence. See #17415.
        sequence_sql = connections[using].ops.sequence_reset_sql(no_style(), [Site])
        if sequence_sql:
            if verbosity >= 2:
                print("Resetting sequence")
            with connections[using].cursor() as cursor:
                for command in sequence_sql:
                    cursor.execute(command)


def connect_signals():
    post_save.connect(
        clear_site_cache_for_author,
        sender=Author,
        dispatch_uid="clear_site_cache_for_author",
    )
