from webquills.sites.models import Site
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.template import engines
from django.test import RequestFactory, TestCase

from .models import LinkCategory, Link

engine = engines["django"]


class TestLinkManager(TestCase):
    fixtures = ("test_linkmgr",)

    @classmethod
    def setUpTestData(cls) -> None:
        site = Site.objects.get(id=1)
        cls.category = LinkCategory.objects.get(id=1)
        cls.fakerequest = RequestFactory().get("/")
        cls.fakerequest.site = site

    def test_iterate_category(self):
        try:
            for link in self.category:
                assert hasattr(link, "get_absolute_url")
        except BaseException:
            assert False

    def test_subscript_category(self):
        assert isinstance(self.category[0], Link)
        assert len(self.category[0:]) == 3

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

    def test_partial_template(self):
        template = engine.get_template(self.category.partial_template)
        out = template.render({"module": self.category, "request": self.fakerequest})
        assert "Test Links" in out
        assert "link1" in out
        assert "link2" in out
        assert "link3" in out
