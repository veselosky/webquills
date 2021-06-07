from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


class SitesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "webquills.sites"
    label = "sites"
    verbose_name = _("Webquills sites")

    def ready(self) -> None:
        # Once the ORM is initialized, connect signal handlers
        from . import signals

        signals.connect_signals()
        post_migrate.connect(signals.create_default_site, sender=self)
