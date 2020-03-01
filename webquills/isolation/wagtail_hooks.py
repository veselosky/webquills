"""
These hooks change the default visiblity of objects so that one tenant (represented by
a Group) cannot see objects belonging to another tenant.
"""
from functools import reduce

from wagtail.core import hooks
from wagtail.core.models import (
    Collection,
    GroupCollectionPermission,
    GroupPagePermission,
)


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
        return collections & descendant_querysets[0]
    # The more complex case, user has multiple roots
    allowedqs = reduce(lambda x, y: x | y, descendant_querysets)
    return collections & allowedqs


def filter_documents_in_permitted_collections(documents, request):
    if request.user.is_superuser:
        return documents
    collections = get_user_collections(request.user)
    return documents.filter(collection__in=collections)


def filter_images_in_permitted_collections(images, request):
    if request.user.is_superuser:
        return images
    collections = get_user_collections(request.user)
    return images.filter(collection__in=collections)


def filter_pages_by_group_permission(pages, request):
    if request.user.is_superuser:
        return pages
    groups = request.user.groups.all()
    permits = GroupPagePermission.objects.filter(group__in=groups)
    querysets = [p.page.get_descendants(inclusive=True) for p in permits]
    # The common case, user has only one root
    if len(querysets) == 1:
        return pages & querysets[0]
    # The more complex case, user has multiple roots
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
