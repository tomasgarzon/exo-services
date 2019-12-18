from django.contrib import admin

from . import models


class ConsultantAdmin(admin.ModelAdmin):
    search_fields = ('user__full_name',)
    list_filter = ('status', 'public_sites')
    list_display = (
        'user',
        'get_roles',
        'get_languages',
        'primary_phone',
        'secondary_phone',
        'status',
        'created',
    )

    def get_roles(self, obj):
        roles = obj.consultant_roles.all().values_list('certification_role__name', flat=True)
        return '/'.join([str(i) for i in roles])

    def get_languages(self, obj):
        langs = obj.languages.all().values_list('name', flat=True)
        return '/'.join([str(i) for i in langs])


class ConsultantValidationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'created',
    )


class ConsultantValidationStatusAdmin(admin.ModelAdmin):
    list_filter = ('status',)
    list_display = (
        'consultant',
        'user_from',
        'validation',
        'content_type',
        'content_object',
        'object_id',
        'status',
        'created',
    )


class BulkCreationAdmin(admin.ModelAdmin):
    list_display = (
        'file_csv',
        'created_by',
        'created',
    )


class BulkCreationConsultantAdmin(admin.ModelAdmin):
    search_fields = ('consultant__user__full_name', 'name', 'email')
    list_filter = ('status',)
    list_display = (
        'consultant',
        'name',
        'email',
        'coins',
        'status',
        'created',
    )


class ConsultantExOProfileAdmin(admin.ModelAdmin):
    search_fields = ('consultant__user__full_name', 'personal_mtp', 'mtp_mastery')
    list_display = (
        'consultant',
        'personal_mtp',
        'mtp_mastery',
        'availability',
        'availability_hours',
        'video_url',
        'created',
    )


class ContractingDataAdmin(admin.ModelAdmin):
    list_display = (
        'profile',
        'name',
        'address',
        'company_name',
        'created',
    )


admin.site.register(models.Consultant, ConsultantAdmin)
admin.site.register(models.ConsultantValidationStatus, ConsultantValidationStatusAdmin)
admin.site.register(models.ConsultantValidation, ConsultantValidationAdmin)
admin.site.register(models.ContractingData, ContractingDataAdmin)
admin.site.register(models.BulkCreation, BulkCreationAdmin)
admin.site.register(models.BulkCreationConsultant, BulkCreationConsultantAdmin)
admin.site.register(models.ConsultantExOProfile, ConsultantExOProfileAdmin)
