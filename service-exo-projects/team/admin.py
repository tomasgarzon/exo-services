from django.contrib import admin

from .models import Team, TeamStep, UserTeamRole


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'stream')
    list_filter = ('project', )


class TeamStepAdmin(admin.ModelAdmin):
    list_display = ('team', 'step')


class TeamRoleAdmin(admin.ModelAdmin):
    list_filter = ('team', )
    list_display = ('team', 'role', 'level')


class UserTeamRoleAdmin(admin.ModelAdmin):
    list_filter = ('team',)
    list_display = ('team', 'user', 'project', 'role')


admin.site.register(Team, TeamAdmin)
admin.site.register(TeamStep, TeamStepAdmin)
admin.site.register(UserTeamRole, UserTeamRoleAdmin)
