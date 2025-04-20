"""
Validation routines for webquills sites.
"""

import idna
from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

sites_config = apps.get_app_config("sites")

# Some error messages for the form validation
normalized_domain_too_long = _(
    "International domain names must be 145 characters or less after normalization. "
    "This domain normalizes to '%(normalized_domain)s', which is %(length)s characters."
)
domain_not_available = _("This domain name is not available.")


def normalize_domain(domain: str) -> str:
    """Normalize a domain name according to RFC 3986 and RFC 3987."""
    domain = domain.strip().lower().rstrip(".")  # Remove trailing dots and lowercase
    domain = idna.encode(domain).decode("ascii")  # Convert to Punycode if needed
    return domain


def validate_subdomain(subdomain: str) -> None:
    """Validate a subdomain name according to RFC 3986 and RFC 3987."""
    # Check if the domain is valid
    try:
        normalized_subdomain = normalize_domain(subdomain)
    except idna.IDNAError:
        raise ValidationError(_("Invalid domain name.")) from None

    # The length of the display name should already have been checked by the
    # CharField, so if we trip this condition, the name contains unicode characters
    # that made it too long when normalized to Punycode.
    if len(normalized_subdomain) > 145:
        raise ValidationError(
            normalized_domain_too_long,
            code="normalized_domain_too_long",
            params={
                "normalized_domain": normalized_subdomain,
                "length": len(normalized_subdomain),
            },
        )
    # Check if the subdomain is reserved
    if normalized_subdomain in sites_config.reserved_names:
        raise ValidationError(domain_not_available, code="domain_not_available")
