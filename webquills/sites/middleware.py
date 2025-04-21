from urllib.parse import urlparse, urlunparse
from django.http.response import HttpResponseNotFound
from django.shortcuts import redirect

from .models import Domain


class SitesMiddleware(object):
    """
    The SitesMiddleware looks up the Domain for this request and maps it to a Site,
    setting attributes on the request for both. If the Domain is not Primary for the
    Site, the middleware will redirect to the Primary Domain.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.domain = Domain.objects.get_for_request(request)
        if request.domain is None:
            return HttpResponseNotFound()
        request.site = request.domain.site
        if request.domain.is_primary:
            return self.get_response(request)
        # Redirect to primary domain if not already there
        to = urlparse(request.build_absolute_uri())
        to = to._replace(netloc=request.site.primary_domain.normalized_domain)
        to = urlunparse(to)
        return redirect(to)
