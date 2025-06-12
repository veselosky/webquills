from django.db import models
from django.utils.translation import gettext_lazy as _

from webquills.models import BaseLayout


class CleanBlogSiteTheme(models.Model):
    """
    The Clean Blog theme for WebQuills.
    This model is used to store the theme settings for the Clean Blog theme.
    """

    site = models.OneToOneField(
        "sites.Site",
        on_delete=models.CASCADE,
        related_name="cleanblog_theme",
        verbose_name=_("Site"),
    )

    class Meta:
        verbose_name = _("Clean Blog Site Theme")
        verbose_name_plural = _("Clean Blog Site Themes")

    def __str__(self):
        return f"Clean Blog Theme for {self.site.name}"

    def get_layout_for(self, obj, request=None):
        """
        Returns the layout for the given object.
        This method is used to get the layout for the Clean Blog theme.
        """
        # For now, we'll return a generic layout for all objects just for testing.
        return BaseLayout(template="cleanblog/index.html", obj=obj)


# Next we create a Layout class for each of the models: ArticleSeries, Article,
# Section, Page, and HomePage.


class CleanBlogArticleSeriesLayout(BaseLayout, models.Model):
    """
    The layout for the ArticleSeries model.
    This model stores object-specific data for the template.
    """

    template = "webquills/themes/cleanblog/article_series.html"

    article_series = models.OneToOneField(
        "commoncontent.ArticleSeries",
        on_delete=models.CASCADE,
        related_name="cleanblog_layout",
        verbose_name=_("Article Series"),
    )

    class Meta:
        verbose_name = _("Clean Blog Article Series Layout")
        verbose_name_plural = _("Clean Blog Article Series Layouts")

    def __str__(self):
        return f"Clean Blog Layout for {self.article_series.title}"


class CleanBlogArticleLayout(BaseLayout, models.Model):
    """
    The layout for the Article model.
    This model stores object-specific data for the template.
    """

    template = "webquills/themes/cleanblog/article.html"

    article = models.OneToOneField(
        "commoncontent.Article",
        on_delete=models.CASCADE,
        related_name="cleanblog_layout",
        verbose_name=_("Article"),
    )

    class Meta:
        verbose_name = _("Clean Blog Article Layout")
        verbose_name_plural = _("Clean Blog Article Layouts")

    def __str__(self):
        return f"Clean Blog Layout for {self.article.title}"


class CleanBlogSectionLayout(BaseLayout, models.Model):
    """
    The layout for the Section model.
    This model stores object-specific data for the template.
    """

    template = "webquills/themes/cleanblog/section.html"

    section = models.OneToOneField(
        "commoncontent.Section",
        on_delete=models.CASCADE,
        related_name="cleanblog_layout",
        verbose_name=_("Section"),
    )

    class Meta:
        verbose_name = _("Clean Blog Section Layout")
        verbose_name_plural = _("Clean Blog Section Layouts")

    def __str__(self):
        return f"Clean Blog Layout for {self.section.title}"


class CleanBlogPageLayout(BaseLayout, models.Model):
    """
    The layout for the Page model.
    This model stores object-specific data for the template.
    """

    template = "webquills/themes/cleanblog/page.html"

    page = models.OneToOneField(
        "commoncontent.Page",
        on_delete=models.CASCADE,
        related_name="cleanblog_layout",
        verbose_name=_("Page"),
    )

    class Meta:
        verbose_name = _("Clean Blog Page Layout")
        verbose_name_plural = _("Clean Blog Page Layouts")

    def __str__(self):
        return f"Clean Blog Layout for {self.page.title}"


class CleanBlogHomePageLayout(BaseLayout, models.Model):
    """
    The layout for the HomePage model.
    This model stores object-specific data for the template.
    """

    template = "webquills/themes/cleanblog/home.html"

    homepage = models.OneToOneField(
        "commoncontent.HomePage",
        on_delete=models.CASCADE,
        related_name="cleanblog_layout",
        verbose_name=_("Home Page"),
    )

    class Meta:
        verbose_name = _("Clean Blog Home Page Layout")
        verbose_name_plural = _("Clean Blog Home Page Layouts")

    def __str__(self):
        return f"Clean Blog Layout for {self.homepage.title}"
