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
