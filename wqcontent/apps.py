from django.apps import AppConfig, apps
from django.utils.translation import gettext_lazy as _


class WqcontentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wqcontent"
    verbose_name = _("1. WebQuills Content")

    # ========================================================================
    # Our configs
    # ========================================================================
    base_template = "posh/base.html"
    # List of blocks in the base template that include other templates, and can
    # be overridden on a per-view basis or with SiteVars.
    base_blocks = (
        "header_template",
        "precontent_template",
        "content_template",
        "postcontent_template",
        "footer_template",
    )
    bootstrap_container_class = "container"
    pagebreak_separator = "<!-- pagebreak -->"
    paginate_by = 15
    paginate_orphans = 2

    # Default block templates are injected to the template context by our context
    # processor, so they're accessible even to 3rd party views.
    header_template = "posh/blocks/header_simple.html"
    footer_template = "posh/blocks/footer_simple.html"

    detail_precontent_template = "posh/blocks/empty.html"
    detail_content_template = "posh/blocks/article_text.html"
    detail_postcontent_template = "posh/blocks/empty.html"

    # TODO list_precontent_template should probably be a custom block, not article_text
    list_precontent_template = "posh/blocks/article_text.html"
    list_content_template = "posh/blocks/article_list_blog.html"
    list_postcontent_template = "posh/blocks/empty.html"

    default_icon = "file-text"
    fallback_copyright = _("© Copyright {} {}. All rights reserved.")

    def as_dict(self) -> dict:
        return {
            "base_template": self.base_template,
            "default_icon": self.default_icon,
            "detail_content_template": self.detail_content_template,
            "detail_precontent_template": self.detail_precontent_template,
            "detail_postcontent_template": self.detail_postcontent_template,
            "footer_template": self.footer_template,
            "header_template": self.header_template,
            "list_content_template": self.list_content_template,
            "list_postcontent_template": self.list_postcontent_template,
            "list_precontent_template": self.list_precontent_template,
            "paginate_by": self.paginate_by,
            "paginate_orphans": self.paginate_orphans,
        }


# A context processor to add our vars to template contexts:
def context_defaults(request):
    """Supply default context variables for templates"""
    # User could have installed a custom appconfig rather than using the default one
    # above, so always fetch it from Django.
    conf = apps.get_app_config("wqcontent")
    # Grab all the default configurations as a dictionary.
    gvars = conf.as_dict()

    # Grab all the site vars from the DB and add them to the dictionary, overriding any
    # fallback defaults.
    gvars.update(request.site.vars.all().values_list("name", "value"))

    # Set the content blocks based on whether the current view is a list or detail view
    # (using a simple heuristic to determine listness.)
    view = request.resolver_match.func
    # For function-based views, check the name for obvious prefix/suffix
    name = view.__name__
    is_list = "_list" in name or name.startswith("list_")
    # For class-based views, the func name is "view". Check for inheritence of List features.
    if hasattr(view, "view_class"):
        from django.views.generic.list import MultipleObjectMixin

        is_list = isinstance(view.view_class, MultipleObjectMixin)

    if is_list:
        gvars["content_template"] = gvars["list_content_template"]
        gvars["precontent_template"] = gvars["list_precontent_template"]
        gvars["postcontent_template"] = gvars["list_postcontent_template"]
    else:
        gvars["content_template"] = gvars["detail_content_template"]
        gvars["precontent_template"] = gvars["detail_precontent_template"]
        gvars["postcontent_template"] = gvars["detail_postcontent_template"]

    # And don't forget to return the value!!!
    return gvars
