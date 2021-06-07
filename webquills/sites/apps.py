from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SitesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "webquills.sites"
    label = "wqsites"
    verbose_name = _("Webquills sites")

    def ready(self) -> None:
        # Once the ORM is initialized, connect signal handlers
        from . import signals

        signals.connect_signals()