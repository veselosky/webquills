from webquills.sites.models import Site
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.template import engines
from django.test import RequestFactory, TestCase

from .models import LinkCategory, Link

engine = engines["django"]


class TestLinkManager(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        site = Site.objects.create(domain="test.com", name="Test")
        cls.category = LinkCategory.objects.create(
            name="Test Links",
            site=site,
            slug="test-links",
        )
        cls.category.links.add(
            Link(text="link1", url="http://example.com/1"),
            Link(text="link2", url="http://example.com/2"),
            Link(text="link3", url="http://example.com/3"),
            bulk=False,
        )
        cls.fakerequest = RequestFactory().get("/")
        cls.fakerequest.site = site

    def test_template_tag(self):
        tpl = "{% load links %}{% link_category category.slug %}"
        template = engine.from_string(tpl)
        out = template.render({"category": self.category, "request": self.fakerequest})
        assert "Test Links" in out
        assert "link1" in out
        assert "link2" in out
        assert "link3" in out

    def test_cached_include(self):
        tpl = """{% include "links/category_links.html" %}"""
        template = engine.from_string(tpl)
        out = template.render(
            {"category_slug": self.category.slug, "request": self.fakerequest}
        )
        assert "Test Links" in out
        assert "link1" in out
        assert "link2" in out
        assert "link3" in out
        # template include should cache itself
        key = make_template_fragment_key(
            "category_links", [self.category.site_id, self.category.slug]
        )
        assert cache.get(key) == out
        # cache should expire on save
        self.category.save()
        assert not cache.get(key)
