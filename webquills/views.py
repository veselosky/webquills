"""
WebQuills inherits and extends the views from django-commoncontent, adding support for
themes and other customizations.
"""

from commoncontent import views as commoncontent_views
from django.conf import settings


class HomePageView(commoncontent_views.HomePageView):
    """
    Home page view for WebQuills.
    """

    template_name = "webquills/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["theme"] = self.request.site.theme
        layout = self.request.site.theme.get_layout_for(
            self.get_object(), request=self.request
        )
        return layout.get_context_data(**context)

    def get_template_names(self):
        """
        Returns the template names for the home page view.
        This method is used to get the template names for the home page view.
        """
        names = super().get_template_names()
        layout = self.request.site.theme.get_layout_for(
            self.get_object(), request=self.request
        )
        # Layout templates take precedence over the default templates.
        return layout.get_template_names() + names
