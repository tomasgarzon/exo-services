from django.contrib import admin

# Register your models here.
from . import models


@admin.register(models.QASession)
class QASessionAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'project',
        'start_at', 'end_at',
        'created',
    )


@admin.register(models.QASessionTeam)
class QASessionTeamAdmin(admin.ModelAdmin):
    list_display = (
        'team', 'session',
        'created',
    )


@admin.register(models.QASessionAdvisor)
class QASessionAdvisorAdmin(admin.ModelAdmin):
    list_display = (
        'qa_session', 'consultant_project_role',
        'created',
    )
