from django.contrib import admin

from . import models


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'location', 'timezone', 'place_id')


admin.site.register(models.Customer, CustomerAdmin)
