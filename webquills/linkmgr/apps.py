from django.apps import AppConfig


class LinkmgrConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "webquills.linkmgr"
    # Hack: admin sorts apps by verbose name. Pull this to top.
    verbose_name = "2. Link manager"
