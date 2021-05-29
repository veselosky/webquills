from django.contrib import admin

from .models import Link, LinkCategory


class LinkInline(admin.StackedInline):
    fields = ("icon", "text", "url")
    model = Link


class LinkCategoryAdmin(admin.ModelAdmin):
    fields = ("site", "name", "slug")
    inlines = (LinkInline,)
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(LinkCategory, LinkCategoryAdmin)
