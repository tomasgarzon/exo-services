from django.contrib import admin

from . import models


class ProjectAdmin(admin.ModelAdmin):
    list_filter = ('status', )
    list_display = (
        'uuid',
        'name',
        'start',
        'end',
        'location',
        'place_id',
        'status',
        'created_by',
    )


class ProjectSettingsAdmin(admin.ModelAdmin):
    list_filter = ('project', )
    list_display = (
        'project',
        'launch',
    )


class ProjectRoleAdmin(admin.ModelAdmin):
    list_filter = ('project', )
    list_display = ('project', 'role', 'level')


class UserProjectRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role')


class StepAdmin(admin.ModelAdmin):
    list_filter = ('project', )
    list_display = (
        'name',
        'project',
        'index',
    )


admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.ProjectRole, ProjectRoleAdmin)
admin.site.register(models.Step, StepAdmin)
admin.site.register(models.ProjectSettings, ProjectSettingsAdmin)
admin.site.register(models.StepStream)
admin.site.register(models.UserProjectRole, UserProjectRoleAdmin)
