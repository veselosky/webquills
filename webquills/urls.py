from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.views.generic.base import RedirectView as Redirect

from webquills.core import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("mce/recent_images.json", views.tiny_image_list, name="mce-recent-images"),
    path("", views.homepage, name="home"),
    # For SEO, redirect page 1 to index
    path("archive/", Redirect.as_view(url="/", permanent=True)),
    path("archive/1/", Redirect.as_view(url="/", permanent=True)),
    path("archive/<int:pagenum>/", views.archive, name="archive"),
    path("feed/", views.SiteFeed(), name="site-feed"),
    path("<slug>/feed/", views.CategoryFeed(), name="category-feed"),
    # These patterns are very generic, so keep last in list
    path("<category_slug>/", views.category, name="category"),
    # For SEO, redirect page 1 to index
    path(
        "<category_slug>/1/",
        Redirect.as_view(url="/%(category_slug)s/", permanent=True),
    ),
    path("<category_slug>/<int:pagenum>/", views.category, name="category_archive"),
    path("<category_slug>/<article_slug>/", views.article, name="article"),
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
