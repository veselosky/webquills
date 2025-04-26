from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.test import TestCase, override_settings

from webquills.sites.actions import (
    create_default_groups_and_perms,
    create_site,
    update_site,
)
from webquills.sites.models import Domain
from webquills.sites.validators import ValidationError

User = get_user_model()


@override_settings(WEBQUILLS_ROOT_DOMAIN="testserver")
class TestActions(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.root_domain = "testserver"
        self.site_config = {"root_domain": self.root_domain}

    def test_create_default_groups_and_perms(self):
        create_default_groups_and_perms()
        group = Group.objects.get(name="regular_user")
        site_content_type = ContentType.objects.get(app_label="sites", model="site")
        permissions = ["add_site", "change_site", "view_site"]
        for perm in permissions:
            self.assertTrue(
                group.permissions.filter(
                    codename=perm, content_type=site_content_type
                ).exists()
            )

    def test_create_site_success(self):
        site_name = "Test Site"
        subdomain = "test"
        site = create_site(self.user, site_name, subdomain)
        self.assertEqual(site.name, site_name)
        self.assertEqual(site.subdomain, subdomain)
        self.assertEqual(site.owner, self.user)
        self.assertTrue(
            Domain.objects.filter(
                site=site,
                display_domain=f"{subdomain}.{self.root_domain}",
                is_canonical=True,
                is_primary=True,
            ).exists()
        )
        self.assertTrue(Group.objects.filter(name=f"site:{subdomain}").exists())

    def test_create_site_invalid_subdomain(self):
        with self.assertRaises(ValidationError):
            create_site(self.user, "Invalid Site", "invalid_subdomain!")

    def test_update_site_success(self):
        site = create_site(self.user, "Old Site", "oldsubdomain")
        updated_site = update_site(site, "Updated Site", "newsubdomain")
        self.assertEqual(updated_site.name, "Updated Site")
        self.assertEqual(updated_site.subdomain, "newsubdomain")
        self.assertTrue(
            Domain.objects.filter(
                site=updated_site,
                display_domain=f"newsubdomain.{self.root_domain}",
                is_canonical=True,
            ).exists()
        )
        self.assertTrue(Group.objects.filter(name="site:newsubdomain").exists())

    def test_update_site_invalid_subdomain(self):
        site = create_site(self.user, "Old Site", "oldsubdomain")
        with self.assertRaises(ValidationError):
            update_site(site, "Updated Site", "invalid_subdomain!")

    def test_create_site_duplicate_subdomain(self):
        create_site(self.user, "Site 1", "duplicate")
        with self.assertRaises(IntegrityError):
            create_site(self.user, "Site 2", "duplicate")
