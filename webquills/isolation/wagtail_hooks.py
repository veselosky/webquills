"""
These hooks change the default visiblity of objects so that one tenant (represented by
a Group) cannot see objects belonging to another tenant. Users cannot see any objects
unless their group has been given explicit permission.
"""
from functools import reduce

from wagtail.core import hooks
from wagtail.core.models import (
    Collection,
    GroupCollectionPermission,
    GroupPagePermission,
)


# As of 2.8, Wagtail does not have a construct_collection_chooser_queryset hook
# that we can hook this to. We have to hack it in by overriding a template.
def get_user_collections(user):
    """
    Returns a queryset of collections for which the user has any explicit group
    permission.
    """
    collections = Collection.objects.all()
    if user.is_superuser:
        return collections

    groups = user.groups.all()
    if not groups:
        # FIXME Will this cause crashes?
        return None

    permits = GroupCollectionPermission.objects.filter(group__in=groups)
    if not permits:
        # FIXME Will this cause crashes?
        return None

    # Collections are heirarchical, and permissions assigned to a parent apply
    # to its descendants.
    descendant_querysets = [
        p.collection.get_descendants(inclusive=True) for p in permits
    ]
    # The common case, user has only one root
    if len(descendant_querysets) == 1:
        # Querysets override bitwise &; collection must pass both filters
        # https://docs.djangoproject.com/en/3.0/ref/models/querysets/#and
        return collections & descendant_querysets[0]
    # The more complex case, user has multiple roots
    # https://docs.djangoproject.com/en/3.0/ref/models/querysets/#or
    allowedqs = reduce(lambda x, y: x | y, descendant_querysets)
    return collections & allowedqs


def filter_documents_in_permitted_collections(documents, request):
    """Filter a document queryset to documents belonging to collections where the
    user has some explicit permission."""
    if request.user.is_superuser:
        return documents
    collections = get_user_collections(request.user)
    return documents.filter(collection__in=collections)


def filter_images_in_permitted_collections(images, request):
    """Filter an image queryset to images belonging to collections where the
    user has some explicit permission."""
    if request.user.is_superuser:
        return images
    collections = get_user_collections(request.user)
    return images.filter(collection__in=collections)


def filter_pages_by_group_permission(pages, request):
    """Filter a pages queryset to trees where the user has some explicit permission."""
    if request.user.is_superuser:
        return pages

    groups = request.user.groups.all()
    if not groups:
        # FIXME Will this cause crashes?
        return None

    permits = GroupPagePermission.objects.filter(group__in=groups)
    if not permits:
        # FIXME Will this cause crashes?
        return None

    querysets = [p.page.get_descendants(inclusive=True) for p in permits]
    # The common case, user has only one root
    if len(querysets) == 1:
        # https://docs.djangoproject.com/en/3.0/ref/models/querysets/#and
        return pages & querysets[0]
    # The more complex case, user has multiple roots
    # https://docs.djangoproject.com/en/3.0/ref/models/querysets/#or
    allowedqs = allowedqs = reduce(lambda x, y: x | y, querysets)
    return pages & allowedqs


def filter_explorer_by_group_permission(parent_page, pages, request):
    return filter_pages_by_group_permission(pages, request)


hooks.register(
    "construct_document_chooser_queryset", filter_documents_in_permitted_collections
)
hooks.register(
    "construct_image_chooser_queryset", filter_images_in_permitted_collections
)
hooks.register("construct_page_chooser_queryset", filter_pages_by_group_permission)
hooks.register("construct_explorer_page_queryset", filter_explorer_by_group_permission)
