"""
Business logic in this app is implemented using a CQRS style. Commands should
be implemented as functions here. Queries should be implemented as methods on
Django model managers. Commands can then be called from a management command
(i.e. the CLI), a view, a signal, etc.
"""
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from wagtail.core.models import Page, Site
from webquills.core.models import HomePage

def initialize_site():
    """
    For development environments, set up the Site and home page objects.
    """
    try:
        site = Site.objects.get(is_default_site=True)
    except Site.DoesNotExist:
        # To create a site, you must first create a root page for it.
        # Seems backwards but it is the wagtail way.
        root = Page.get_first_root_node()
        content_type = ContentType.objects.get_for_model(
            HomePage
        )
        homepage = HomePage(
            title=settings.WAGTAIL_SITE_NAME,
            draft_title=settings.WAGTAIL_SITE_NAME,
            slug="root",
            content_type=content_type,
            show_in_menus=True
        )
        root.add_child(instance=homepage)
        # Create a site with the new homepage set as the root
        # Note: this is the wagtail Site model, not django's
        return Site.objects.create(
            hostname="webquills.com",
            root_page=homepage,
            is_default_site=True,
            site_name=settings.WAGTAIL_SITE_NAME,
        )

    # If the default site was already created, just update its properties
    site.hostname = "webquills.com"
    site.site_name = settings.WAGTAIL_SITE_NAME
    site.port = 8000
    site.save()

    if not isinstance(site.root_page, HomePage):
        # Still has the default blank wagtail page, replace it
        root = Page.get_first_root_node()
        content_type = ContentType.objects.get_for_model(
            HomePage
        )
        homepage = HomePage(
            title=settings.WAGTAIL_SITE_NAME,
            draft_title=settings.WAGTAIL_SITE_NAME,
            slug="root",
            content_type=content_type,
            show_in_menus=True
        )
        root.add_child(instance=homepage)
        site.root_page = homepage
        site.save()