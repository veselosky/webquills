from importlib.util import find_spec
from django.conf import settings
from django.urls import include, path
from django.contrib import admin


urlpatterns = [
    path("admin/", admin.site.urls),
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
