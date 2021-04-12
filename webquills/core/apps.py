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

    def get_default_image_size(self):
        return (1000, 1000)

    def get_image_media_dir(self):
        return "uploads"
