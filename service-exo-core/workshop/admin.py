from django.contrib import admin    # NOQA

from .models import WorkShop


class WorkShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'start', 'end', 'location', 'timezone', 'place_id')


admin.site.register(WorkShop, WorkShopAdmin)
