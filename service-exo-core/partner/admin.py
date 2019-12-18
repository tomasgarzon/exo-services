from django.contrib import admin

from . import models


class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'location', 'timezone', 'place_id')


admin.site.register(models.Partner, PartnerAdmin)
