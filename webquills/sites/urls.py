from django.urls import path

from webquills.sites.views import SiteCreateView, SiteListView, SiteUpdateView

urlpatterns = [
    path("", SiteListView.as_view(), name="site_list"),
    path("create/", SiteCreateView.as_view(), name="site_create"),
    path("<int:pk>/", SiteUpdateView.as_view(), name="site_update"),
]
