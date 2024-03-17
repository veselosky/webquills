from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.views.generic.base import RedirectView as Redirect

from wqcontent import buildable_views as generic


urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("account/", include("allauth.urls")),
    path("<slug:section_slug>/feed/", Redirect.as_view(pattern_name="section_feed")),
    path("feed/", Redirect.as_view(pattern_name="site_feed")),
    # URLs below can be statically generated.
    # Home page pagination needs to come before the other page patterns to match.
    path("page_<int:page>.html", generic.HomePageView.as_view(), name="home_paginated"),
    path(
        "<slug:section_slug>/page_<int:page>.html",
        generic.SectionView.as_view(),
        name="section_paginated",
    ),
    path(
        "<slug:section_slug>/<slug:article_slug>.html",
        generic.ArticleDetailView.as_view(),
        name="article_page",
    ),
    path(
        "<slug:page_slug>.html", generic.PageDetailView.as_view(), name="landing_page"
    ),
    path("<slug:section_slug>/", generic.SectionView.as_view(), name="section_page"),
    path("<slug:section_slug>/index.rss", generic.SectionFeed(), name="section_feed"),
    path("index.rss", generic.SiteFeed(), name="site_feed"),
    path("", generic.HomePageView.as_view(), name="home_page"),
]

if settings.DEBUG:
    # NOTE: When DEBUG and staticfiles is installed, Django automatically adds static
    # urls, but does not automatically serve MEDIA
    from django.conf.urls.static import static

    # Serve static and media files from development server
    # urlpatterns += staticfiles_urlpatterns()  # automatic when DEBUG on
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    try:
        import debug_toolbar

        # Article pattern was matching and blocking these when appended, hence insert
        urlpatterns.insert(0, path("__debug__/", include(debug_toolbar.urls)))
    except ImportError:
        pass
