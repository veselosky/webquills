###############################################################################
# To prevent circular import problems, DO NOT import anything from the app
# itself at the module level. Instead, import within a method if necessary,
# e.g. `ready` (which is the correct place to wire signal handlers).
###############################################################################
from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class CoreConfig(AppConfig):
    name = "webquills.core"
    # The default label "core" conflicts with wagtail.core, so we will call
    # ourselves...
    label = "webquills"
    # Hack: admin sorts apps by verbose name. Pull this to top.
    verbose_name = _("1. Webquills")

    def get_default_image_size(self):
        return (1000, 1000)

    def get_image_media_dir(self):
        return "uploads"

    @property
    def pagelength(self):
        if hasattr(settings, "WEBQUILLS_PAGELENGTH"):
            return getattr(settings, "WEBQUILLS_PAGELENGTH")
        return 25

    @property
    def homepage_featured_tag(self):
        if hasattr(settings, "WEBQUILLS_HOMEPAGE_FEATURED_TAG"):
            return getattr(settings, "WEBQUILLS_HOMEPAGE_FEATURED_TAG")
        return "hpfeatured"

    @property
    def featured_tag(self):
        if hasattr(settings, "WEBQUILLS_FEATURED_TAG"):
            return getattr(settings, "WEBQUILLS_FEATURED_TAG")
        return "featured"

    @property
    def num_featured(self):
        if hasattr(settings, "WEBQUILLS_NUM_FEATURED"):
            return getattr(settings, "WEBQUILLS_NUM_FEATURED")
        return 4
