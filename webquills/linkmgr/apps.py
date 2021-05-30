from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LinkmgrConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "webquills.linkmgr"
    # Hack: admin sorts apps by verbose name. Pull this to top.
    verbose_name = _("2. Link manager")
