from django.contrib import admin

from .models import Site, Domain


admin.site.register(Site)
admin.site.register(Domain)
