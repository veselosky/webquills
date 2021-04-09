"""
Some template tags and filters, mostly for site navigation.

The get_site_root tag was removed. Use the core tag `wagtail_site` instead.
https://docs.wagtail.io/en/stable/topics/writing_templates.html#wagtail-site
"""
from django import template


# https://docs.djangoproject.com/en/3.0/howto/custom-template-tags/
register = template.Library()


@register.filter
def active_if_ancestor_of(page, current_page):
    """For nav menu, returns ' active' (note the space) if given page is an ancestor of
    the current page (or IS the current page).
    """
    if current_page.url_path.startswith(page.url_path):
        return " active"
    return ""
