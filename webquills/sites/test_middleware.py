from unittest.mock import MagicMock, patch
from urllib.parse import urlparse

from django.http import HttpResponse, HttpResponseNotFound
from django.test import RequestFactory, TestCase

from webquills.sites.middleware import SitesMiddleware


class TestSitesMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = MagicMock(return_value=HttpResponse("OK"))
        self.middleware = SitesMiddleware(self.get_response)

    @patch("webquills.sites.models.Domain.objects.get_for_request")
    def test_no_domain_found(self, mock_get_for_request):
        # Simulate no domain found
        mock_get_for_request.return_value = None

        request = self.factory.get("/")
        with self.assertLogs("webquills.sites.middleware", "WARNING") as log:
            response = self.middleware(request)
            self.assertIn(
                "No domain found for request",
                log.output[0],
            )

        self.assertIsInstance(response, HttpResponseNotFound)
        mock_get_for_request.assert_called_once_with(request)

    @patch("webquills.sites.models.Domain.objects.get_for_request")
    def test_primary_domain(self, mock_get_for_request):
        # Simulate a primary domain
        mock_domain = MagicMock()
        mock_domain.is_primary = True
        mock_domain.site = MagicMock()
        mock_get_for_request.return_value = mock_domain

        request = self.factory.get("/")
        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)
        self.get_response.assert_called_once_with(request)
        self.assertEqual(request.domain, mock_domain)
        self.assertEqual(request.site, mock_domain.site)

    @patch("webquills.sites.models.Domain.objects.get_for_request")
    def test_redirect_to_primary_domain(self, mock_get_for_request):
        # Simulate a non-primary domain
        mock_domain = MagicMock()
        mock_domain.is_primary = False
        mock_domain.site = MagicMock()
        mock_domain.site.primary_domain.normalized_domain = "primary.com"
        mock_get_for_request.return_value = mock_domain

        request = self.factory.get("/", HTTP_HOST="nonprimary.com")
        response = self.middleware(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.url).netloc, "primary.com")
        mock_get_for_request.assert_called_once_with(request)
