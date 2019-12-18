from django.contrib import admin

from .models import ExOHub


@admin.register(ExOHub)
class ExOHubAdmin(admin.ModelAdmin):
    list_filter = ('_type',)
    list_display = ('name', '_type', 'order', 'created')
