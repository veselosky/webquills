from django.contrib import admin

from webquills.core import models


class PageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ["headline"]}


# Bare minimum, below customize as needed
admin.site.register(models.ArticlePage, PageAdmin)
admin.site.register(models.CallToAction)
admin.site.register(models.CategoryPage, PageAdmin)
admin.site.register(models.CopyrightLicense)
admin.site.register(models.HomePage, PageAdmin)
admin.site.register(models.Image)
admin.site.register(models.SiteMeta)
