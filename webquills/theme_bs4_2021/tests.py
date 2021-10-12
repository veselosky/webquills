from django.contrib.auth.models import User
from django.template import engines
from django.test import RequestFactory, TestCase

from webquills.sites.models import Site
from webquills.linkmgr.models import LinkCategory
from webquills.theme_bs4_2021 import context_processors
from webquills.theme_bs4_2021.models import Theme, ThemeModule, ModuleList


engine = engines["django"]


class TestTheme(TestCase):
    fixtures = ("test_copyrightable", "test_linkmgr")

    @classmethod
    def setUpTestData(cls) -> None:
        site = Site.objects.get(id=1)
        cls.fakerequest = RequestFactory().get("/")
        cls.fakerequest.site = site

    def test_context_processor_custom(self):
        """
        The CP should inject the theme assign to the site and marked as
        "active" in the DB.
        """
        theme = Theme.objects.create(name="Test Theme 1", site_id=1, is_active=True)
        ctx = context_processors.theme(self.fakerequest)
        assert ctx["theme"].name == "Test Theme 1"

    def test_context_processor_default(self):
        """
        If no theme is assigned to a site, the CP should create a default theme.
        """
        ctx = context_processors.theme(self.fakerequest)
        assert ctx["theme"].name == "Default theme"

    def test_context_processor_inactive_theme(self):
        """
        The CP should ignore themes not marked as "active" in the DB.
        """
        theme = Theme.objects.create(name="Test Theme 1", site_id=1)
        ctx = context_processors.theme(self.fakerequest)
        assert ctx["theme"].name == "Default theme"

    def test_module_list_iteration(self):
        """
        A ModuleList should be iterable, and should iterate the includable modules,
        not the intermediate ThemeModule objects (which just store pointers).
        """
        # Create 2 link categories and make them modules in a module list
        one = LinkCategory.objects.create(name="Cat One", slug="cat-one", site_id=1)
        two = LinkCategory.objects.create(name="Cat Two", slug="cat-two", site_id=1)
        modlist = ModuleList.objects.create(name="My List", slug="my-list")
        first = ThemeModule.objects.create(module=one, module_list=modlist)
        second = ThemeModule.objects.create(module=two, module_list=modlist)

        # Now the actual test
        my_list = ModuleList.objects.get(slug="my-list")
        assert my_list[0] == one
        assert my_list[0:] == [one, two]
        for thing in my_list:
            assert isinstance(thing, LinkCategory)

    def test_theme_defaults(self):
        theme = Theme(site=Site.objects.get(id=1))
        assert theme.sidebar_modules == []
        assert theme.footer_modules == []
        menu = theme.nav_menu
        # should return a queryset of CategoryPage by default
        assert menu.count() == 1

    def test_custom_sidebar(self):
        cat = LinkCategory.objects.get(id=1)
        modlist = ModuleList.objects.create(name="My List", slug="my-list")
        first = ThemeModule.objects.create(module=cat, module_list=modlist)
        theme = Theme.objects.create(
            name="Test Theme 1", site_id=1, custom_sidebar=modlist
        )
        assert theme.sidebar_modules == modlist

    def test_custom_nav_menu(self):
        cat = LinkCategory.objects.get(id=1)
        theme = Theme.objects.create(
            name="Test Theme 1", site_id=1, custom_nav_menu=cat
        )
        assert theme.nav_menu == cat

    def test_nav_menu_template(self):
        cat = LinkCategory.objects.get(id=1)
        theme = Theme.objects.create(
            name="Test Theme 1", site_id=1, custom_nav_menu=cat
        )
        template = engine.get_template("components/navmenu_top.html")
        out = template.render({"theme": theme, "request": self.fakerequest})
        assert "link1" in out


class TestAdmins(TestCase):
    fixtures = ("test_users",)

    def setUp(self) -> None:
        self.client.force_login(User.objects.get(username="superuser"))

    def test_theme_add(self):
        url = "/admin/bs4theme/theme/add/"
        resp = self.client.get(url)
        assert resp.status_code == 200

    def test_theme_list(self):
        url = "/admin/bs4theme/theme/"
        resp = self.client.get(url)
        assert resp.status_code == 200

    def test_modulelist_add(self):
        url = "/admin/bs4theme/modulelist/add/"
        resp = self.client.get(url)
        assert resp.status_code == 200

    def test_modulelist_list(self):
        url = "/admin/bs4theme/modulelist/"
        resp = self.client.get(url)
        assert resp.status_code == 200
