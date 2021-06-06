from django import template

from webquills.core.models import Image


# https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/
register = template.Library()


@register.simple_tag
def image_url(instance: Image, op: str = "", **kwargs):
    if op:
        return instance.get_thumb(op, **kwargs).url
    elif kwargs:
        raise ValueError(
            "image_url called without op. Did you for get to quote the operation name?"
        )
    return instance.file.url


@register.simple_tag(takes_context=True)
def menu_active(context, menuitem: str):
    path = str(context["request"].path)
    # Special case because every url starts with /
    if menuitem == "/":
        if path == "/":
            return "btn btn-outline-primary"
        return ""
    # Otherwise, if the page is under the menupage's directory, it is active
    if path.startswith(menuitem):
        return "btn btn-outline-primary"
    return ""
