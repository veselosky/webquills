from django.http.response import HttpResponseNotFound
from .models import Domain


class SitesMiddleware(object):
    """
    The SitesMiddleware looks up the Domain for this request and maps it to a Site,
    setting attributes on the request for both. If the Domain is not Primary for the
    Site, AND the Site is entitled to the CustomDomain Feature, the middleware will
    redirect to the Primary Domain. If the Domain is not entitled to the CustomDomain
    Feature, the middleware will respond with a ResponseNotFound, short-circuiting the
    request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        assert not hasattr(request, "domain"), "Domain attribute already set on request"
        request.domain = Domain.objects.get_for_request(request)
        if request.domain is None:
            return HttpResponseNotFound()
        return self.get_response(request)
