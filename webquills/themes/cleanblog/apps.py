from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CleanblogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "webquills.themes.cleanblog"
    label = "cleanblog"
    verbose_name = _("Clean Blog")
    webquills_theme = True

    def get_theme_for_site(self, site):
        """
        Returns the theme for the given site.
        This method is used to determine which theme to use for a specific site.
        """
        CleanBlogSiteTheme = self.get_model("CleanBlogSiteTheme")
        try:
            return CleanBlogSiteTheme.objects.get(site=site)
        except CleanBlogSiteTheme.DoesNotExist:
            # If the theme does not exist, create one (without saving).
            return CleanBlogSiteTheme(site=site)
