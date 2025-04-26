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


class WebQuillsViewTestCase(TestCase):
    """
    Base test case for views in the webquills app.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        actions.create_default_groups_and_perms()
        # Create a test user and assign them to the regular_user group
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.user.groups.add(Group.objects.get(name="regular_user"))
        cls.user.save()
        # For the middleware to pass through the request, must be able to look up domain
        cls.site = actions.create_site(
            cls.user, name="Default Site for CMS Tests", subdomain="cmstest"
        )
        Domain.objects.create(
            site=cls.site,
            display_domain="testserver",
            normalized_domain="testserver",
            is_primary=True,
        )


@override_settings(WEBQUILLS_ROOT_DOMAIN="testserver")
class SiteCreateViewTests(WebQuillsViewTestCase):
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
        self.assertEqual(domain.display_domain, "test.testserver")
        self.assertEqual(domain.normalized_domain, "test.testserver")

    def test_form_valid_handles_database_error(self):
        with patch("django.contrib.auth.models.Group.objects.create") as mock_create:
            mock_create.side_effect = DatabaseError
            resp = self.client.post(reverse("site_create"), data=self.valid_data)
        self.assertContains(resp, domain_not_available)
        # Check that the site was not created
        self.assertFalse(Site.objects.filter(name="Test Site").exists())


@override_settings(WEBQUILLS_ROOT_DOMAIN="testserver")
class SiteUpdateViewTests(WebQuillsViewTestCase):
    def setUp(self):
        self.client.force_login(self.user)
        self.valid_data = {
            "name": "Updated Site",
            "subdomain": "updated",
        }

    def test_form_valid_updates_site_and_group(self):
        site = actions.create_site(self.user, name="Test Site", subdomain="test")
        response = self.client.post(
            reverse("site_update", args=[site.pk]), data=self.valid_data
        )
        self.assertEqual(response.status_code, 302)  # Redirect on success
        # Get a fresh copy from DB
        site.refresh_from_db()
        self.assertEqual(site.name, "Updated Site")
        self.assertEqual(site.subdomain, "updated")
        self.assertEqual(site.normalized_subdomain, "updated")
        self.assertEqual(site.group.name, "site:updated")
        self.assertEqual(Domain.objects.filter(site=site).count(), 1)
        self.assertEqual(
            Domain.objects.get(site=site).display_domain, "updated.testserver"
        )
        self.assertEqual(site.canonical_domain.display_domain, "updated.testserver")
        self.assertEqual(site.canonical_domain.normalized_domain, "updated.testserver")

    def test_form_valid_handles_database_error(self):
        site = actions.create_site(self.user, name="Test Site", subdomain="test")
        with patch("webquills.sites.views.update_site", side_effect=DatabaseError):
            resp = self.client.post(
                reverse("site_update", args=[site.pk]), data=self.valid_data
            )
        self.assertContains(resp, domain_not_available)
        site.refresh_from_db()
        self.assertEqual(site.name, "Test Site")  # No changes applied
