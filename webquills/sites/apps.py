from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _


class SitesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "webquills.sites"
    label = "sites"
    verbose_name = _("Webquills sites")

    def ready(self) -> None:
        # Once the ORM is initialized, connect signal handlers
        pass

    @property
    def root_domain(self) -> str:
        """
        Returns the root domain for the application. This is the domain from which the
        publishing tools are served, and all sites have a subdomain of this domain.
        For example, if the root domain is "example.com", a site with the name
        "site1" will have a domain of "site1.example.com".
        """
        root = getattr(settings, "WEBQUILLS_ROOT_DOMAIN", None)
        if not root:
            raise ImproperlyConfigured(
                "WEBQUILLS_ROOT_DOMAIN setting not set. This is required for the WebQuills "
                "application to function correctly."
            )
        return root

    @property
    def reserved_names(self) -> list[str]:
        """
        Returns a list of reserved names that cannot be used as subdomains.
        """
        reserved = getattr(settings, "WEBQUILLS_RESERVED_SUBDOMAINS", [])
        # This is a list of names that are reserved for use by the application.
        # For example, "www" and "admin" are often reserved for use by the application.
        # reserved += [
        #     "www",
        #     "admin",
        #     "api",
        #     "static",
        #     "media",
        #     "assets",
        # ]
        return reserved
