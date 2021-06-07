"""
These are mostly smoke tests to ensure the admin classes do not crash if I mess up.
"""
from django.test import TestCase
from django.contrib.auth.models import User


class TestAdmins(TestCase):
    fixtures = ["test_users", "creative_commons", "test_copyrightable"]

    def setUp(self) -> None:
        self.client.force_login(User.objects.get(username="superuser"))

    def test_homepage_list(self):
        url = "/admin/webquills/homepage/"
        resp = self.client.get(url)
        assert resp.status_code == 200

    def test_homepage_add(self):
        url = "/admin/webquills/homepage/add/"
        resp = self.client.get(url)
        assert resp.status_code == 200

    def test_categorypage_list(self):
        url = "/admin/webquills/categorypage/"
        resp = self.client.get(url)
        assert resp.status_code == 200

    def test_categorypage_add(self):
        url = "/admin/webquills/categorypage/add/"
        resp = self.client.get(url)
        assert resp.status_code == 200

    def test_articlepage_list(self):
        url = "/admin/webquills/articlepage/"
        resp = self.client.get(url)
        assert resp.status_code == 200

    def test_articlepage_add(self):
        url = "/admin/webquills/articlepage/add/"
        resp = self.client.get(url)
        assert resp.status_code == 200

    def test_author_list(self):
        url = "/admin/webquills/author/"
        resp = self.client.get(url)
        assert resp.status_code == 200

    def test_author_add(self):
        url = "/admin/webquills/author/add/"
        resp = self.client.get(url)
        assert resp.status_code == 200

    def test_sites_list(self):
        url = "/admin/sites/site/"
        resp = self.client.get(url)
        assert resp.status_code == 200

    def test_sites_add(self):
        url = "/admin/sites/site/add/"
        resp = self.client.get(url)
        assert resp.status_code == 200

    def test_image_list(self):
        url = "/admin/webquills/image/"
        resp = self.client.get(url)
        assert resp.status_code == 200

    def test_image_add(self):
        url = "/admin/webquills/image/add/"
        resp = self.client.get(url)
        assert resp.status_code == 200

    def test_copyrightlicense_list(self):
        url = "/admin/webquills/copyrightlicense/"
        resp = self.client.get(url)
        assert resp.status_code == 200

    def test_copyrightlicense_add(self):
        url = "/admin/webquills/copyrightlicense/add/"
        resp = self.client.get(url)
        assert resp.status_code == 200
