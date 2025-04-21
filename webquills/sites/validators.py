"""
Validation routines for webquills sites.
"""

import idna
from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

sites_config = apps.get_app_config("sites")

# Some error messages for the form validation
subdomain_too_long = _("Subdomain names must be 63 characters or less.")
domain_not_available = _("This domain name is not available.")


def normalize_domain(domain: str) -> str:
    """Normalize a domain name according to RFC 3986 and RFC 3987."""
    domain = domain.strip().lower().rstrip(".")  # Remove trailing dots and lowercase
    domain = idna.encode(domain).decode("ascii")  # Convert to Punycode if needed
    return domain


def validate_subdomain(subdomain: str) -> None:
    """Validate a subdomain name according to RFC 3986 and RFC 3987."""
    # Check some obvious stuff first
    if not subdomain:
        raise ValidationError(
            _("Subdomain must not be empty."),
            code="subdomain_empty",
            params={"subdomain": subdomain},
        )
    if "." in subdomain:
        raise ValidationError(
            _("Subdomains must not contain dots."),
            code="subdomain_contains_dots",
            params={"subdomain": subdomain},
        )
    # Length is constrained by RFC1035 to 63 characters
    if len(subdomain) > 63:
        raise ValidationError(
            _("Subdomain must be 63 characters or less."),
            code="subdomain_too_long",
            params={"subdomain": subdomain},
        )
    # Check if the subdomain is reserved
    if subdomain in sites_config.reserved_names:
        raise ValidationError(
            domain_not_available,
            code="domain_not_available",
            params={"subdomain": subdomain},
        )

    # Check if the domain is valid
    try:
        normalize_domain(subdomain)
    except idna.IDNAError as e:
        raise ValidationError(_("Invalid domain name.")) from e
