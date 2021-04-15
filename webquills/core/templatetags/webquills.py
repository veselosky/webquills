from django import template

from webquills.core.images import Image


# https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/
register = template.Library()


@register.simple_tag
def image_url(instance: Image, op: str = "", **kwargs):
    if op:
        return instance.get_thumb(op, **kwargs).url
    return instance.file.url
