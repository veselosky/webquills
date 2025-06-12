from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseLayout:
    """
    Base class for all layouts. Note that BaseLayout is not a model. It can be
    instantiated on its own, or used as a mixin with a Django model. For templates
    that are not tied to a specific model, or that don't need any object-specific data,
    you can use this class directly by passing a template, object, and optional context
    to the constructor.
    """

    def __init__(self, template, obj, context=None):
        """
        Initializes the layout with the given template.
        :param template: The template to use for the layout.
        """
        self.template = template
        self.object = obj
        self.context = context or {}

    def get_context_data(self, **context):
        """
        Returns the context data for the layout.
        This method is used to get the context data for the template.
        """
        return self.context

    def get_template_names(self):
        """
        Returns the template names for the layout.
        This method is used to get the template names for the layout.
        """
        return [self.template]
