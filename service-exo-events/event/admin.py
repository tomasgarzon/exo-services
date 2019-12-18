from django.contrib import admin

from . import models


class EventAdmin(admin.ModelAdmin):
    list_filter = ('category', '_status')
    list_display = ('title', 'slug', 'category', '_status', 'created')
    search_fields = ('title', 'location')


class InterestedAdmin(admin.ModelAdmin):
    list_display = ('event', 'name', 'email', 'created')
    search_fields = ('event__title', 'email')


class ParticipantAdmin(admin.ModelAdmin):
    list_filter = ('exo_role', 'status')
    list_display = ('user_name', 'user_email', 'event', 'exo_role', 'status', 'created')
    search_fields = ('event__title', 'email')


admin.site.register(models.Event, EventAdmin)
admin.site.register(models.Interested, InterestedAdmin)
admin.site.register(models.Participant, ParticipantAdmin)
