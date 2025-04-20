from django import forms
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import DatabaseError
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, UpdateView

from webquills.sites.actions import create_site, update_site
from webquills.sites.models import Site
from webquills.sites.validators import (
    domain_not_available,
    normalize_domain,
    validate_subdomain,
)

sites_config = apps.get_app_config("sites")


class SiteListView(LoginRequiredMixin, ListView):
    """
    Let's the user view a list of their (unarchived) sites.
    """

    model = Site
    template_name = "sites/site_list.html"
    context_object_name = "sites"
    paginate_by = 10  # FIXME: Get from settings

    def get_queryset(self):
        return Site.objects.for_user(self.request.user).filter(archived_date=None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_count"] = self.get_queryset().count()
        return context


class SiteEditForm(forms.ModelForm):
    """
    Form used to create/update a Site instance.
    """

    class Meta:
        model = Site
        fields = ["name", "subdomain"]

    def clean_subdomain(self):
        """Validate the subdomain field to ensure it is a valid domain name."""
        subdomain = self.cleaned_data["subdomain"]
        # Validate the subdomain using the custom validator
        validate_subdomain(subdomain)

        normalized_subdomain = normalize_domain(subdomain)

        dupe_subdomain = Site.objects.filter(
            subdomain=normalized_subdomain, archive_date=None
        )
        if self.instance.pk:
            dupe_subdomain.exclude(pk=self.instance.pk)
        if dupe_subdomain.exists():
            raise forms.ValidationError(
                domain_not_available, code="domain_not_available"
            )

        self.cleaned_data["normalized_subdomain"] = normalized_subdomain
        return subdomain


class SiteCreateView(PermissionRequiredMixin, CreateView):
    """
    The SiteCreateView is responsible for creating a new Site instance and its
    associated objects. Each Site also must have a Domain and a Group.
    """

    # Note: although this View creates a Group and a Domain, the user does not need
    # permission to create those objects. We create them implicitly as a side effect.
    permission_required = "sites.add_site"
    permission_denied_message = _("You do not have permission to create a site.")
    form_class = SiteEditForm
    model = Site
    template_name = "sites/site_form.html"
    success_url = reverse_lazy("site_list")

    def form_valid(self, form):
        """Handle the form submission and create the Site instance."""

        subdomain = form.cleaned_data["subdomain"]
        name = form.cleaned_data["name"]

        try:
            self.object = create_site(
                user=self.request.user,
                name=name,
                subdomain=subdomain,
            )

        # If there's a problem creating the site or its related objects, the
        # create_site function will propagate the DatabaseError. We catch it
        # here and add it to the form errors.
        except DatabaseError:
            form.add_error(
                "subdomain",
                _("This domain name is not available."),
            )
            return self.form_invalid(form)

        return HttpResponseRedirect(self.get_success_url())


class SiteUpdateView(PermissionRequiredMixin, UpdateView):
    """The SiteUpdateView is responsible for updating a Site instance and its
    associated objects. Each Site also must have a Domain and a Group.
    """

    permission_required = "sites.change_site"
    permission_denied_message = _("You do not have permission to update this site.")
    model = Site
    form_class = SiteEditForm
    template_name = "sites/site_form.html"
    success_url = reverse_lazy("site_list")

    def get_queryset(self):
        """Constrain queryset to user's sites."""
        return Site.objects.filter(group__in=self.request.user.groups.all())

    def form_valid(self, form):
        """Handle the form submission and update the Site instance."""
        try:
            update_site(
                site=self.object,
                name=form.cleaned_data["name"],
                subdomain=form.cleaned_data["subdomain"],
            )
        # If there's a problem updating the site or its related objects, the
        # update_site function will propagate the DatabaseError. We catch it
        # here and add it to the form errors.
        except DatabaseError:
            form.add_error(
                "subdomain",
                _("This domain name is not available."),
            )
            return self.form_invalid(form)
        return super().form_valid(form)
