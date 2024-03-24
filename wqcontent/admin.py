from django.contrib import admin

from .models import Article, HomePage, Image, Page, Section



#######################################################################################
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    readonly_fields = ("width", "height", "mime_type")
    fields = (
        "title",
        "image_file",
        "site",
        "alt_text",
        "tags",
        "description",
        "custom_copyright_holder",
        "custom_copyright_notice",
        "date_created",
        "width",
        "height",
        "mime_type",
    )


#######################################################################################
class CreativeWorkAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "date_published"
    list_display = ("title", "date_published", "site", "status")
    list_filter = ("site", "status")
    search_fields = ("title", "description")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "site",
                    "status",
                    "date_published",
                    "description",
                    "share_image",
                    "body",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "expires",
                    "seo_title",
                    "seo_description",
                    "content_template",
                    "base_template",
                )
            },
        ),
        (
            "Additional metadata",
            {
                "classes": ("collapse",),
                "fields": ("custom_icon", "custom_copyright_notice"),
            },
        ),
    )


#######################################################################################
@admin.register(Article)
class ArticleAdmin(CreativeWorkAdmin):
    list_display = ("title", "section", "date_published", "site", "status")
    list_filter = ("section", "site", "status")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "site",
                    "section",
                    "status",
                    "date_published",
                    "author_display_name",
                    "author_profile_url",
                    "description",
                    "share_image",
                    "tags",
                    "body",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "expires",
                    "seo_title",
                    "seo_description",
                    "content_template",
                    "base_template",
                )
            },
        ),
        (
            "Additional metadata",
            {
                "classes": ("collapse",),
                "fields": ("type", "locale", "custom_icon", "custom_copyright_notice"),
            },
        ),
    )


#######################################################################################
@admin.register(Section)
class SectionAdmin(CreativeWorkAdmin):
    pass


#######################################################################################
@admin.register(Page)
class PageAdmin(CreativeWorkAdmin):
    pass


#######################################################################################
@admin.register(HomePage)
class HomePageAdmin(CreativeWorkAdmin):
    pass
