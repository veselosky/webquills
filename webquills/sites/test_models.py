import unittest

from django.contrib.auth.models import Group, User
from django.test import RequestFactory, TestCase, override_settings

from webquills.sites import actions
from webquills.sites.models import BlockReason, Domain, Site


@override_settings(WEBQUILLS_ROOT_DOMAIN="example.com")
class TestSiteManager(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.site = actions.create_site(self.user, "Test Site", "test")
        self.alt_domain = Domain.objects.create(
            site=self.site,
            display_domain="alt.example.com",
            normalized_domain="alt.example.com",
            is_primary=False,
            is_canonical=False,
        )

    def test_get_for_request(self):
        request = RequestFactory().get("/")
        request.get_host = lambda: "test.example.com"

        site = Site.objects.get_for_request(request)
        self.assertEqual(site, self.site)

    def test_get_for_request_alt_domain(self):
        request = RequestFactory().get("/")
        request.get_host = lambda: "alt.example.com"

        site = Site.objects.get_for_request(request)
        self.assertEqual(site, self.site)

    def test_get_for_request_with_port(self):
        request = RequestFactory().get("/")
        request.get_host = lambda: "test.example.com:8080"

        site = Site.objects.get_for_request(request)
        self.assertEqual(site, self.site)

    def test_get_for_request_archived_site(self):
        self.site.archive_date = "2023-01-01"
        self.site.save()

        request = RequestFactory().get("/")
        request.get_host = lambda: "test.example.com"

        site = Site.objects.get_for_request(request)
        self.assertIsNone(site)

    def test_get_for_request_site_blocked(self):
        reason = BlockReason.objects.create(
            name="Testing",
            description="Blocked for testing purposes",
        )
        self.site.block_reason = reason
        self.site.save()

        request = RequestFactory().get("/")
        request.get_host = lambda: "test.example.com"

        site = Site.objects.get_for_request(request)
        self.assertIsNone(site)

    def test_get_for_request_no_match(self):
        request = RequestFactory().get("/")
        request.get_host = lambda: "nonexistent.example.com"

        site = Site.objects.get_for_request(request)
        self.assertIsNone(site)


@override_settings(WEBQUILLS_ROOT_DOMAIN="example.com")
class TestSiteQuerySet(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        alt_user = User.objects.create_user(username="altuser")
        self.site1 = actions.create_site(self.user, "Site 1", "site1")
        self.site2 = actions.create_site(self.user, "Site 2", "site2")
        self.site3 = actions.create_site(alt_user, "Site 3", "site3")

    def test_ids_for_user(self):
        site_ids = Site.objects.all().ids_for_user(self.user)
        self.assertEqual(site_ids, [self.site1.id, self.site2.id])

    def test_for_user(self):
        sites = Site.objects.all().for_user(self.user)
        self.assertCountEqual(sites, [self.site1, self.site2])


@override_settings(WEBQUILLS_ROOT_DOMAIN="example.com")
class TestDomainManager(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.site = actions.create_site(self.user, "Test Site", "test")

    def test_get_for_request_primary_domain(self):
        request = RequestFactory().get("/")
        request.get_host = lambda: "test.example.com"

        domain = Domain.objects.get_for_request(request)
        self.assertEqual(domain, self.site.primary_domain)

    def test_get_for_request_with_port(self):
        request = RequestFactory().get("/")
        request.get_host = lambda: "test.example.com:8080"

        domain = Domain.objects.get_for_request(request)
        self.assertEqual(domain, self.site.primary_domain)

    def test_get_for_request_archived_site(self):
        self.site.archive_date = "2023-01-01"
        self.site.save()

        request = RequestFactory().get("/")
        request.get_host = lambda: "test.example.com"

        domain = Domain.objects.get_for_request(request)
        self.assertIsNone(domain)

    def test_get_for_request_site_blocked(self):
        reason = BlockReason.objects.create(
            name="Testing",
            description="Blocked for testing purposes",
        )
        self.site.block_reason = reason
        self.site.save()

        request = RequestFactory().get("/")
        request.get_host = lambda: "test.example.com"

        domain = Domain.objects.get_for_request(request)
        self.assertIsNone(domain)

    def test_get_for_request_no_match(self):
        request = RequestFactory().get("/")
        request.get_host = lambda: "nonexistent.example.com"

        domain = Domain.objects.get_for_request(request)
        self.assertIsNone(domain)


class TestDomainModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.site = actions.create_site(self.user, "Test Site", "test")

    def test_save_normalizes_domain(self):
        domain = Domain.objects.create(
            site=self.site,
            display_domain="ExAmPlE.CoM",
        )
        self.assertEqual(domain.normalized_domain, "example.com")

    def test_save_updates_primary_flag(self):
        primary_domain = Domain.objects.create(
            site=self.site,
            display_domain="primary.com",
            is_primary=True,
        )
        new_primary_domain = Domain.objects.create(
            site=self.site,
            display_domain="newprimary.com",
            is_primary=True,
        )
        primary_domain.refresh_from_db()
        self.assertFalse(primary_domain.is_primary)
        self.assertTrue(new_primary_domain.is_primary)

    def test_save_updates_canonical_flag(self):
        canonical_domain = Domain.objects.create(
            site=self.site,
            display_domain="canonical.com",
            is_canonical=True,
        )
        new_canonical_domain = Domain.objects.create(
            site=self.site,
            display_domain="newcanonical.com",
            is_canonical=True,
        )
        canonical_domain.refresh_from_db()
        self.assertFalse(canonical_domain.is_canonical)
        self.assertTrue(new_canonical_domain.is_canonical)


if __name__ == "__main__":
    unittest.main()
