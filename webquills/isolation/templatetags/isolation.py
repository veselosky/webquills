from django import template

from webquills.isolation import wagtail_hooks

register = template.Library()


@register.simple_tag(takes_context=True)
def get_user_collections(context):
    request = context.get("request")
    return wagtail_hooks.get_user_collections(request.user)
