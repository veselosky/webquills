from django.conf import settings
from django.urls import include, re_path, path
from django.contrib import admin

from coderedcms import admin_urls as coderedadmin_urls
from coderedcms import search_urls as coderedsearch_urls
from coderedcms import urls as codered_urls
from wagtail.documents import urls as wagtaildocs_urls


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(coderedadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", include(coderedsearch_urls)),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    try:
        import debug_toolbar

        urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
    except ImportError:
        pass

    # Serve static and media files from development server
    # urlpatterns += staticfiles_urlpatterns()  # allegedly automatic when DEBUG on
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    re_path(r"", include(codered_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    url(r'^pages/', include(wagtail_urls)),
]
