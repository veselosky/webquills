"""
This is a library for storing business logic. It is a set of functions that operate on
models, potentially in complex ways, encapsulating the business logic for the
higher-level application. The actions could then be called from views, management
commands, celery tasks, etc. This allows for a clean separation of concerns and makes the code
easier to maintain and test.
"""

from __future__ import annotations

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Model

from webquills.sites.models import Domain, Site
from webquills.sites.validators import normalize_domain, validate_subdomain

User = get_user_model()
sites_config = apps.get_app_config("sites")


def create_default_groups_and_perms():
    """
    Create default groups and permissions for the Site model.
    """
    group, created = Group.objects.get_or_create(name="regular_user")
    site_content_type = ContentType.objects.get(app_label="sites", model="site")
    permissions = [
        "add_site",
        "change_site",
        "view_site",
    ]
    for perm in permissions:
        permission = Permission.objects.get(
            codename=perm, content_type=site_content_type
        )
        group.permissions.add(permission)


def create_site(user: Model, name: str, subdomain: str) -> Site:
    """
    Create a new site with the given name and subdomain.

    :param user: The user who owns the site.
    :param name: The name of the site.
    :param subdomain: The subdomain of the site.
    :return: The created Site object.
    :raises ValidationError: If the subdomain is not valid.
    :raises DatabaseError: If there is a database error while creating the site.
    """
    # Validate the subdomain using the custom validator
    validate_subdomain(subdomain)
    normalized_subdomain = normalize_domain(subdomain)
    group_name = f"site:{normalized_subdomain}"
    domain = f"{subdomain}.{sites_config.root_domain}"
    normalized_domain = f"{normalized_subdomain}.{sites_config.root_domain}"

    with transaction.atomic():
        # Create the Group instance
        group = Group.objects.create(name=group_name)
        site = Site.objects.create(
            owner=user,
            group=group,
            name=name,
            subdomain=subdomain,
            normalized_subdomain=normalized_subdomain,
        )
        # Create the Domain instance. When a site is first created, its canonical domain
        # is also primary.
        Domain.objects.create(
            site=site,
            display_domain=domain,
            normalized_domain=normalized_domain,
            is_canonical=True,
            is_primary=True,
        )
        # Ensure the Group is added to the user's groups
        group.user_set.add(user)
    return site


def update_site(
    site: Site,
    name: str,
    subdomain: str,
) -> Site:
    """
    Update the given site with the new name and subdomain.

    :param site: The site to update.
    :param name: The new name of the site.
    :param subdomain: The new subdomain of the site.
    :return: The updated Site object.
    :raises ValidationError: If the subdomain is not valid.
    :raises DatabaseError: If there is a database error while updating the site.
    """
    # Validate the subdomain using the custom validator
    validate_subdomain(subdomain)
    normalized_subdomain = normalize_domain(subdomain)
    group_name = f"site:{normalized_subdomain}"
    domain = f"{subdomain}.{sites_config.root_domain}"
    normalized_domain = f"{normalized_subdomain}.{sites_config.root_domain}"

    with transaction.atomic():
        # Update the Site instance
        site.name = name

        # Update the Group name if needed
        if site.group.name != group_name:
            site.group.name = group_name
            site.group.save()

        # Update the domain
        if site.subdomain != subdomain:
            site.subdomain = subdomain
            site.normalized_subdomain = normalized_subdomain
            # Update the Domain instance
            domain_instance = Domain.objects.get(site=site, is_canonical=True)
            domain_instance.display_domain = domain
            domain_instance.normalized_domain = normalized_domain
            domain_instance.save()
        site.save()

    return site
