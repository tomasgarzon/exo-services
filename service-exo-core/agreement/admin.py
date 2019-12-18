from django.contrib import admin

from . import models


class AgreementAdmin(admin.ModelAdmin):
    list_filter = ('status', 'domain')
    list_display = (
        'name',
        'version',
        'recipient',
        'domain',
        'status',
        'created',
    )


class UserAgreementAdmin(admin.ModelAdmin):
    list_filter = ('status', 'agreement')
    search_fields = ('user__full_name',)
    list_display = (
        'user',
        'agreement',
        'status',
        'created',
    )


admin.site.register(models.Agreement, AgreementAdmin)
admin.site.register(models.UserAgreement, UserAgreementAdmin)
