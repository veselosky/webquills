from django.contrib import admin, messages
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .models import ModuleList, Theme, ThemeModule


@admin.action(permissions=["change"], description="Make this the active theme")
def make_active(modeladmin, request, queryset):
    if queryset.count() > 1:
        modeladmin.message_user(
            request,
            _("Only one Theme can be active for a given site"),
            messages.ERROR,
        )
    with transaction.atomic():
        # Deactivate the currently active theme
        newtheme = queryset[0]
        modeladmin.get_queryset(request).filter(site=newtheme.site).update(
            is_active=False
        )
        newtheme.is_active = True
        newtheme.save()
    modeladmin.message_user(
        request, _("Theme %(theme)s has been activated") % {"theme": newtheme.name}
    )


class ThemeModuleInline(admin.StackedInline):
    model = ThemeModule


class ModuleListAdmin(admin.ModelAdmin):
    inlines = [ThemeModuleInline]
    prepopulated_fields = {"slug": ("name",)}


class ThemeAdmin(admin.ModelAdmin):
    exclude = ("is_active",)
    list_display = ("name", "site", "is_active")
    list_filter = ("site",)
    actions = (make_active,)


admin.site.register(ModuleList, ModuleListAdmin)
admin.site.register(Theme, ThemeAdmin)
