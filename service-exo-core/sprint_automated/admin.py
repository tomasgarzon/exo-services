from django.contrib import admin

from . import models


class SprintAutomatedAdmin(admin.ModelAdmin):
    list_filter = ('status', )
    list_display = ('name', 'status', 'duration', 'customer', 'created', 'modified')


admin.site.register(models.SprintAutomated, SprintAutomatedAdmin)
