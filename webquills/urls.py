from importlib.util import find_spec

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from webquills import views

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("cms/sites/", include("webquills.sites.urls")),
    path("tinymce/", include("tinymce.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    # path("", include("commoncontent.urls")),
    # Replace the commoncontent views with webquills views
    path(
        "<slug:section_slug>/feed/", RedirectView.as_view(pattern_name="section_feed")
    ),
    path("feed/", RedirectView.as_view(pattern_name="site_feed")),
    # Home page pagination needs to come before the other page patterns to match.
    path("page_<int:page>.html", views.HomePageView.as_view(), name="home_paginated"),
    # path("author/", generic.AuthorListView.as_view(), name="author_list"),
    # path(
    #     "author/<slug:author_slug>/index.rss", generic.AuthorFeed(), name="author_feed"
    # ),
    # path(
    #     "author/<slug:author_slug>/page_<int:page>.html",
    #     generic.AuthorView.as_view(),
    #     name="author_page_paginated",
    # ),
    # path(
    #     "author/<slug:author_slug>/", generic.AuthorView.as_view(), name="author_page"
    # ),
    # path(
    #     "<slug:section_slug>/page_<int:page>.html",
    #     generic.SectionView.as_view(),
    #     name="section_paginated",
    # ),
    # path(
    #     "<slug:section_slug>/<slug:series_slug>/<slug:article_slug>.html",
    #     generic.ArticleDetailView.as_view(),
    #     name="article_series_page",
    # ),
    # path(
    #     "<slug:section_slug>/<slug:series_slug>/",
    #     generic.ArticleSeriesView.as_view(),
    #     name="series_page",
    # ),
    # path(
    #     "<slug:section_slug>/<slug:article_slug>.html",
    #     generic.ArticleDetailView.as_view(),
    #     name="article_page",
    # ),
    # path(
    #     "<slug:page_slug>.html", generic.PageDetailView.as_view(), name="landing_page"
    # ),
    # path("<slug:section_slug>/", generic.SectionView.as_view(), name="section_page"),
    # path("<slug:section_slug>/index.rss", generic.SectionFeed(), name="section_feed"),
    # path("index.rss", generic.SiteFeed(), name="site_feed"),
    path("", views.HomePageView.as_view(), name="home_page"),
]

if settings.DEBUG:
    # NOTE: When DEBUG and staticfiles is installed, Django automatically adds static
    # urls, but does not automatically serve MEDIA
    from django.conf.urls.static import static

    # Serve static and media files from development server
    # urlpatterns += staticfiles_urlpatterns()  # automatic when DEBUG on
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if find_spec("debug_toolbar"):
        # Article pattern was matching and blocking these when appended, hence insert
        urlpatterns.insert(0, path("__debug__/", include("debug_toolbar.urls")))
