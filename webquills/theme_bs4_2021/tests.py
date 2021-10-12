from django.test import TestCase

from webquills.sites.models import Site
from webquills.linkmgr.models import LinkCategory
from webquills.theme_bs4_2021.models import Theme, ThemeModule, ModuleList


class TestTheme(TestCase):
    fixtures = ("test_copyrightable", "test_linkmgr")

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
