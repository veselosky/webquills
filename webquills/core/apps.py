###############################################################################
# To prevent circular import problems, DO NOT import anything from the app
# itself at the module level. Instead, import within a method if necessary,
# e.g. `ready` (which is the correct place to wire signal handlers).
###############################################################################
from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "webquills.core"
    # The default label "core" conflicts with wagtail.core, so we will call
    # ourselves...
    label = "webquills"
