from django import template
from django.utils.safestring import mark_safe

from webquills.linkmgr.models import LinkCategory


register = template.Library()


@register.inclusion_tag("links/_category.html", takes_context=True)
def link_category(context, slug, title=None):
    site = context["request"].site
    try:
        cat = LinkCategory.objects.get(slug=slug, site=site)
        return {
            "links": cat.links.all(),
            "title": title or cat.name,
            "catslug": cat.slug,
            "site": site,
        }
    except LinkCategory.DoesNotExist:
        return {}
