import unittest
from webquills.sites.models import normalize_domain
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Group
from webquills.sites.models import Site, Domain

# filepath: /Users/vince/Devel/webquills/webquills/sites/test_models.py


class TestNormalizeDomain(unittest.TestCase):
    def test_domain_without_port(self):
        domain = "example.com"
        expected = "example.com"
        self.assertEqual(normalize_domain(domain), expected)

    def test_domain_with_trailing_dots(self):
        domain = "example.com."
        expected = "example.com"
        self.assertEqual(normalize_domain(domain), expected)

    def test_domain_with_mixed_case(self):
        domain = "ExAmPlE.CoM"
        expected = "example.com"
        self.assertEqual(normalize_domain(domain), expected)

    def test_internationalized_domain(self):
        domain = "münchen.de"
        expected = "xn--mnchen-3ya.de"
        self.assertEqual(normalize_domain(domain), expected)


class TestSiteManager(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.group = Group.objects.create(name="example.com")
        self.user.groups.add(self.group)

        self.site = Site.objects.create(
            owner=self.user,
            group=self.group,
            name="Test Site",
        )
        self.domain = Domain.objects.create(
            site=self.site,
            display_domain="example.com",
            normalized_domain="example.com",
            is_primary=True,
        )

    def test_get_for_request(self):
        request = RequestFactory().get("/")
        request.get_host = lambda: "example.com"

        site = Site.objects.get_for_request(request)
        self.assertEqual(site, self.site)

    def test_get_for_request_with_port(self):
        request = RequestFactory().get("/")
        request.get_host = lambda: "example.com:8080"

        site = Site.objects.get_for_request(request)
        self.assertEqual(site, self.site)


class TestSiteQuerySet(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.group1 = Group.objects.create(name="example.com")
        self.group2 = Group.objects.create(name="example.org")
        self.user.groups.add(self.group1)
        self.user.groups.add(self.group2)

        self.site1 = Site.objects.create(
            owner=self.user,
            group=self.group1,
            name="Site 1",
        )
        self.site2 = Site.objects.create(
            owner=self.user,
            group=self.group2,
            name="Site 2",
        )

    def test_ids_for_user(self):
        site_ids = Site.objects.all().ids_for_user(self.user)
        self.assertCountEqual(site_ids, [self.site1.id, self.site2.id])


class TestDomainManager(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.group = Group.objects.create(name="Test Group")
        self.site = Site.objects.create(
            owner=self.user,
            group=self.group,
            name="Test Site",
        )
        self.primary_domain = Domain.objects.create(
            site=self.site,
            display_domain="example.com",
            normalized_domain="example.com",
            is_primary=True,
        )
        self.canonical_domain = Domain.objects.create(
            site=self.site,
            display_domain="canonical.com",
            normalized_domain="canonical.com",
            is_canonical=True,
        )

    def test_get_for_request_primary_domain(self):
        request = RequestFactory().get("/")
        request.get_host = lambda: "example.com"

        domain = Domain.objects.get_for_request(request)
        self.assertEqual(domain, self.primary_domain)

    def test_get_for_request_canonical_domain(self):
        request = RequestFactory().get("/")
        request.get_host = lambda: "canonical.com"

        domain = Domain.objects.get_for_request(request)
        self.assertEqual(domain, self.canonical_domain)

    def test_get_for_request_no_match(self):
        request = RequestFactory().get("/")
        request.get_host = lambda: "nonexistent.com"

        domain = Domain.objects.get_for_request(request)
        self.assertIsNone(domain)


class TestDomainModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.group = Group.objects.create(name="Test Group")
        self.site = Site.objects.create(
            owner=self.user,
            group=self.group,
            name="Test Site",
        )

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
