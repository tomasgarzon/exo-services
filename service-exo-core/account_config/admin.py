# django imports
from django.contrib import admin

# app imports
from . import models


class ConfigParamAdmin(admin.ModelAdmin):
    list_filter = ('group', 'param_type')
    list_display = (
        'name',
        'param_type',
        '_default_value',
        'group',
        'condition_for_available',
        'created',
    )


class ConfigValueAdmin(admin.ModelAdmin):
    list_filter = ('config_parameter',)
    list_display = (
        'user',
        'config_parameter',
        '_value',
    )


admin.site.register(models.ConfigParam, ConfigParamAdmin)
admin.site.register(models.ConfigValue, ConfigValueAdmin)
