from .models import Theme


def theme(request):
    """
    Injects the theme for the current site into the template context.
    """
    candidates = Theme.objects.filter(site=request.site, is_active=True)
    if candidates.exists():
        # there should only be one, but that's not enforced in the DB schema
        return {"theme": candidates[0]}
    else:
        # Use an empty theme with all default values
        return {"theme": Theme(name="Default theme", site=request.site)}
