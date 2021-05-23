from django.contrib import admin

from webquills.core import models


class PageAdmin(admin.ModelAdmin):
    list_display = ("headline", "site", "published", "status")
    list_filter = ("site", "status", "author")
    prepopulated_fields = {"slug": ["headline"]}


class ArticleAdmin(PageAdmin):
    fieldsets = (
        (
            "Metadata",
            {
                "fields": (
                    "site",
                    "author",
                    "status",
                    "published",
                    "updated_at",
                    "category",
                    "tags",
                )
            },
        ),
        (
            "Content",
            {
                "fields": (
                    "seo_description",
                    "featured_image",
                    "headline",
                    "body",
                    "slug",
                )
            },
        ),
        (
            "Overrides",
            {
                "classes": ["collapse"],
                "fields": (
                    "seo_title",
                    "custom_byline",
                    "custom_about",
                    "credits",
                    ("custom_copyright_holder", "custom_copyright_license"),
                    "custom_copyright_notice",
                    "expired",
                ),
            },
        ),
    )


class CategoryAdmin(PageAdmin):
    fieldsets = (
        (
            "Metadata",
            {
                "fields": (
                    "site",
                    "author",
                    "status",
                    "published",
                    "updated_at",
                    "tags",
                )
            },
        ),
        (
            "Content",
            {
                "fields": (
                    "seo_description",
                    "featured_image",
                    "headline",
                    "intro",
                    "slug",
                )
            },
        ),
        (
            "Overrides",
            {
                "classes": ["collapse"],
                "fields": (
                    "seo_title",
                    "custom_byline",
                    "custom_about",
                    "credits",
                    ("custom_copyright_holder", "custom_copyright_license"),
                    "custom_copyright_notice",
                    "expired",
                ),
            },
        ),
    )


class HomePageAdmin(PageAdmin):
    fieldsets = (
        (
            "Metadata",
            {
                "fields": (
                    "site",
                    "author",
                    "status",
                    "published",
                    "updated_at",
                    "tags",
                )
            },
        ),
        (
            "Content",
            {
                "fields": (
                    "seo_description",
                    "featured_image",
                    "headline",
                    "lead",
                    "picture",
                    "action_label",
                    "target_url",
                    "slug",
                )
            },
        ),
        (
            "Overrides",
            {
                "classes": ["collapse"],
                "fields": (
                    "seo_title",
                    "custom_byline",
                    "custom_about",
                    "credits",
                    ("custom_copyright_holder", "custom_copyright_license"),
                    "custom_copyright_notice",
                    "expired",
                ),
            },
        ),
    )


# Bare minimum, below customize as needed
admin.site.register(models.Author)
admin.site.register(models.ArticlePage, ArticleAdmin)
admin.site.register(models.CategoryPage, CategoryAdmin)
admin.site.register(models.CopyrightLicense)
admin.site.register(models.HomePage, HomePageAdmin)
admin.site.register(models.Image)
admin.site.register(models.SiteMeta)
