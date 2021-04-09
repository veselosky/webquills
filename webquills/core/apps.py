###############################################################################
# To prevent circular import problems, DO NOT import anything from the app
# itself at the module level. Instead, import within a method if necessary,
# e.g. `ready` (which is the correct place to wire signal handlers).
###############################################################################
from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    name = "webquills.core"
    # The default label "core" conflicts with wagtail.core, so we will call
    # ourselves...
    label = "webquills"

    def get_image_sizes(self):
        """
        Return a list of image sizes (as (x,y) tuples) to be pre-generated for
        uploaded images.
        """
        if hasattr(settings, "WEBQUILLS_IMAGE_SIZES"):
            return getattr(settings, "WEBQUILLS_IMAGE_SIZES")
        return ((1000, 1000), (300, 300))
