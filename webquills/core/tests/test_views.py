from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from webquills.core.models import ArticlePage, CategoryPage, HomePage, Status


class TestViews(TestCase):
    fixtures = ["test_users", "creative_commons", "test_copyrightable"]

    @classmethod
    def setUpTestData(cls) -> None:
        # Oops, forgot to add a Homepage to my fixture
        cls.homepage = HomePage.objects.create(
            headline="Test Homepage",
            slug="home",
            site_id=1,
            status=Status.USABLE,
            published=timezone.now(),
        )

    def test_home(self):
        url = reverse("home")
        resp = self.client.get(url)
        assert resp.status_code == 200

    def test_recent_images(self):
        url = reverse("mce-recent-images")
        resp = self.client.get(url)
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/json"

    def test_archive_root_redirect(self):
        "archive index should redirect to home"
        url = "/archive/"
        resp = self.client.get(url)
        assert resp.status_code == 301
        assert resp["Location"] == "/"

    def test_archive_p1_redirect(self):
        "archive page 1 should redirect to home"
        url = "/archive/1/"
        resp = self.client.get(url)
        assert resp.status_code == 301
        assert resp["Location"] == "/"

    def test_archive_pagination(self):
        "archive should honor the pagelength setting"
        with self.settings(WEBQUILLS_PAGELENGTH=1):
            url = "/archive/2/"
            resp = self.client.get(url)
            assert resp.status_code == 200

    def test_site_feed(self):
        url = reverse("site-feed")
        resp = self.client.get(url)
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/rss+xml; charset=utf-8"

    def test_category_page(self):
        category = CategoryPage.objects.first()
        url = category.get_absolute_url()
        resp = self.client.get(url)
        assert resp.status_code == 200
        assert category.headline in str(resp.content)

    def test_category_pagination(self):
        "category should honor the pagelength setting"
        category = CategoryPage.objects.first()
        url = category.get_absolute_url()
        with self.settings(WEBQUILLS_PAGELENGTH=1):
            resp = self.client.get(url)
            assert resp.status_code == 200

    def test_category_feed(self):
        category = CategoryPage.objects.first()
        url = reverse("category-feed", kwargs={"slug": category.slug})
        resp = self.client.get(url)
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/rss+xml; charset=utf-8"

    def test_article_view(self):
        article = ArticlePage.objects.first()
        url = article.get_absolute_url()
        resp = self.client.get(url)
        assert resp.status_code == 200
        assert article.headline in str(resp.content)
