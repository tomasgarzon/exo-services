# Register your models here.
from django.contrib import admin

from .models import Invitation


class InvitationAdmin(admin.ModelAdmin):
    list_display = (
        'hash', 'type', 'status', 'user', 'invite_user',
        'created', 'modified',
    )
    list_filter = ('type', 'status')
    search_fields = ('hash', )


admin.site.register(Invitation, InvitationAdmin)
