from unittest.mock import Mock
import time

from django.test import TestCase

from .models import Site


class TestMiddleware(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.ex1 = Site.objects.create(domain="mysite.com", name="mysite.com")
        cls.ex2 = Site.objects.create(domain="sub.mysite.com", name="sub.mysite.com")
        cls.ex3 = Site.objects.create(domain="default.com", name="default.com")

    def test_site_host_match(self):
        req = Mock()
        req.get_host.return_value = "sub.mysite.com"
        with self.settings(SITE_ID=self.ex3.id):
            site = Site.objects._get_for_request(req)
            assert site.domain == "sub.mysite.com"

    def test_site_root_match(self):
        req = Mock()
        req.get_host.return_value = "nosuchsub.mysite.com"
        with self.settings(SITE_ID=self.ex3.id):
            site = Site.objects._get_for_request(req)
            assert site.domain == "mysite.com"

    def test_site_fallback(self):
        req = Mock()
        req.get_host.return_value = "nosuchdomain.com"
        with self.settings(SITE_ID=self.ex3.id):
            site = Site.objects._get_for_request(req)
            assert site.domain == "default.com"

    def test_site_default_match(self):
        req = Mock()
        req.get_host.return_value = "default.com"
        with self.settings(SITE_ID=self.ex3.id):
            site = Site.objects._get_for_request(req)
            assert site.domain == "default.com"
