from django.contrib import admin

from .models import Team


class TeamAdmin(admin.ModelAdmin):
    list_display = ('project', 'name', 'has_meeting_id')
    list_filter = ('project', )


admin.site.register(Team, TeamAdmin)
