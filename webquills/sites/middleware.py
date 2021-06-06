from .models import Site


class SitesMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.site = Site.objects._get_for_request(request)
        return self.get_response(request)
