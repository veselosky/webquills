import unittest
from unittest.mock import patch

from django.core.exceptions import ValidationError
from idna import IDNAError

from webquills.sites.validators import normalize_domain, validate_subdomain


class TestNormalizeDomain(unittest.TestCase):
    def test_domain_without_port(self):
        domain = "example.com"
        expected = "example.com"
        self.assertEqual(normalize_domain(domain), expected)

    def test_domain_with_trailing_dots(self):
        domain = "example.com."
        expected = "example.com"
        self.assertEqual(normalize_domain(domain), expected)

    def test_domain_with_mixed_case(self):
        domain = "ExAmPlE.CoM"
        expected = "example.com"
        self.assertEqual(normalize_domain(domain), expected)

    def test_internationalized_domain(self):
        domain = "münchen.de"
        expected = "xn--mnchen-3ya.de"
        self.assertEqual(normalize_domain(domain), expected)

    def test_domain_with_whitespace(self):
        domain = "  example.com  "
        expected = "example.com"
        self.assertEqual(normalize_domain(domain), expected)

    def test_invalid_domain_raises_idna_error(self):
        with self.assertRaises(IDNAError):
            normalize_domain("invalid_domain_###")


class TestValidateSubdomain(unittest.TestCase):
    def test_valid_subdomain(self):
        subdomain = "example"
        try:
            validate_subdomain(subdomain)  # Should not raise an exception
        except ValidationError:
            self.fail("validate_subdomain raised ValidationError unexpectedly!")

    def test_internationalized_subdomain(self):
        subdomain = "münchen"
        try:
            validate_subdomain(subdomain)  # Should not raise an exception
        except ValidationError:
            self.fail("validate_subdomain raised ValidationError unexpectedly!")

    def test_subdomain_with_dots(self):
        """Subdomains must not contain dots."""
        subdomain = "example.com"
        with self.assertRaises(ValidationError):
            validate_subdomain(subdomain)

    def test_subdomain_too_long(self):
        subdomain = "a" * 64
        with self.assertRaises(ValidationError) as context:
            validate_subdomain(subdomain)
        self.assertEqual(context.exception.code, "subdomain_too_long")

    def test_reserved_subdomain(self):
        # Mocking the reserved_names for testing
        with patch("webquills.sites.apps.SitesConfig.reserved_names", ["reserved"]):
            subdomain = "reserved"
            with self.assertRaises(ValidationError) as context:
                validate_subdomain(subdomain)
            self.assertEqual(context.exception.code, "domain_not_available")

    def test_invalid_subdomain(self):
        subdomain = "invalid_domain_###"
        with self.assertRaises(ValidationError):
            validate_subdomain(subdomain)
