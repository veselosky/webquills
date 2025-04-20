from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import DatabaseError
from django.test import TestCase, override_settings
from django.urls import reverse

from webquills.sites import actions
from webquills.sites.models import Domain, Site
from webquills.sites.validators import domain_not_available

User = get_user_model()


@override_settings(WEBQUILLS_ROOT_DOMAIN="example.com")
class SiteCreateViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        actions.create_default_groups_and_perms()
        # Create a test user and assign them to the regular_user group
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.user.groups.add(Group.objects.get(name="regular_user"))
        cls.user.save()

    def setUp(self):
        self.client.force_login(self.user)
        self.valid_data = {
            "name": "Test Site",
            "subdomain": "test",
        }

    def test_form_valid_creates_site_group_and_domain(self):
        response = self.client.post(reverse("site_create"), data=self.valid_data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        # Check that the site was created
        site = Site.objects.get(name="Test Site")
        # Check that the group was created
        self.assertEqual(site.group.name, "site:test")
        # The user should have been added to the site's group
        self.assertTrue(site.group.user_set.filter(id=self.user.id).exists())
        # Check that the domain was created
        domain = Domain.objects.get(site=site)
        self.assertEqual(domain.display_domain, "test.example.com")
        self.assertEqual(domain.normalized_domain, "test.example.com")

    def test_form_valid_handles_database_error(self):
        with patch("django.contrib.auth.models.Group.objects.create") as mock_create:
            mock_create.side_effect = DatabaseError
            resp = self.client.post(reverse("site_create"), data=self.valid_data)
        self.assertContains(resp, domain_not_available)
        # Check that the site was not created
        self.assertFalse(Site.objects.filter(name="Test Site").exists())


class SiteUpdateViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        actions.create_default_groups_and_perms()
        # Create a test user and assign them to the regular_user group
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.user.groups.add(Group.objects.get(name="regular_user"))
        cls.user.save()

    def setUp(self):
        self.group = Group.objects.create(name="site:test")
        # As the owner, the user would be automatically added to the group
        # when the site is created.
        self.user.groups.add(self.group)
        self.user.save()
        self.user.refresh_from_db()

        self.site = Site.objects.create(
            owner=self.user,
            group=self.group,
            name="Test Site",
            subdomain="test",
            normalized_subdomain="test",
        )
        self.client.force_login(self.user)
        self.valid_data = {
            "name": "Updated Site",
            "subdomain": "updated",
        }

    def test_form_valid_updates_site_and_group(self):
        response = self.client.post(
            reverse("site_update", args=[self.site.pk]), data=self.valid_data
        )
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.site.refresh_from_db()
        self.group.refresh_from_db()
        self.assertEqual(self.site.name, "Updated Site")
        self.assertEqual(self.site.subdomain, "updated")
        self.assertEqual(self.group.name, "site:updated")

    def test_form_valid_handles_database_error(self):
        with patch("webquills.sites.views.update_site", side_effect=DatabaseError):
            resp = self.client.post(
                reverse("site_update", args=[self.site.pk]), data=self.valid_data
            )
        self.assertContains(resp, domain_not_available)
        self.site.refresh_from_db()
        self.assertEqual(self.site.name, "Test Site")  # No changes applied
