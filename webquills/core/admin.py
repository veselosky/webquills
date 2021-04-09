from django.contrib import admin

from webquills.core import models

# Bare minimum, below customize as needed
admin.site.register(models.ArticlePage)
admin.site.register(models.CallToAction)
admin.site.register(models.CategoryPage)
admin.site.register(models.CopyrightLicense)
admin.site.register(models.HomePage)
admin.site.register(models.Image)
admin.site.register(models.SiteMeta)
