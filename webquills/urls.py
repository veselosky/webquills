from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from webquills.core import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("mce/recent_images.json", views.tiny_image_list, name="mce-recent-images"),
    path("", views.homepage, name="home"),
    # These patterns are very generic, so keep last in list
    path("<category_slug>/", views.category, name="category"),
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
