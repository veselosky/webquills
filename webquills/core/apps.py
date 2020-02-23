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


# Set of features to make available in the draftail editor. We exclude
# headings, images, and embeds because we provide blocks for these.
default_richtext_features = (
    "blockquote",
    "bold",
    "code",
    "document-link",
    "hr",
    "italic",
    "link",
    "ol",
    "strikethrough",
    "subscript",
    "superscript",
    "ul",
)
