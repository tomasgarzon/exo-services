from django.contrib import admin

from .models import ExOActivity


@admin.register(ExOActivity)
class ExOActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description', 'order', 'created')
