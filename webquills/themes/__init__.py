from django.apps import apps


def get_theme_choices():
    """
    Returns a list of available themes for the WebQuills application.
    This function is used to populate the theme choices in the Site model.
    """
    themes = []
    for app in apps.get_app_configs():
        if hasattr(app, "webquills_theme") and app.webquills_theme:
            themes.append((app.label, app.verbose_name))
    return sorted(themes, key=lambda x: x[1])
