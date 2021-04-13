from django import template
from django.conf import settings

from webquills.core.images import Image


# https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/
register = template.Library()


@register.simple_tag
def image_url(instance: Image, op: str = "", **kwargs):
    print(f"{instance}, {op}, {kwargs}")
    if op:
        return settings.MEDIA_URL + instance.get_thumb(op, **kwargs)
    return instance.file.url
