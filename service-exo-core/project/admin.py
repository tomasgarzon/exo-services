from django.contrib import admin

from . import models


class StepAdmin(admin.ModelAdmin):
    list_filter = ('status', 'project__lapse')
    list_display = (
        'name', 'short_name',
        'project', 'index',
        'status', 'lapse_type_display',
    )


class ProjectAdmin(admin.ModelAdmin):
    list_filter = ('status', )
    list_display = (
        'uuid',
        'name',
        'type_verbose_name',
        'start',
        'end',
        'location',
        'timezone',
        'place_id',
        'status',
    )


admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Step, StepAdmin)
