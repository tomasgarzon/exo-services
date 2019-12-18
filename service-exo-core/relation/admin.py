from django.contrib import admin

from . import models


@admin.register(models.ConsultantRole)
class ConsultantRoleAdmin(admin.ModelAdmin):
    list_display = (
        'consultant', 'certification_role', 'certification_group', 'created',
    )
    list_filter = ('certification_role',)
    search_fields = (
        'consultant__user__full_name',
        'consultant__user__email',
        'certification_role__name'
    )


@admin.register(models.ConsultantProjectRole)
class ConsultantProjectRoleAdmin(admin.ModelAdmin):
    list_display = (
        'consultant', 'project', 'exo_role', 'exo_role_other_name', 'status', 'visible',
    )
    list_filter = ('exo_role__categories', 'status', 'visible')
    search_fields = ('project__name', 'consultant__user__full_name', 'role__name')


@admin.register(models.UserProjectRole)
class UserProjectRoleAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'project', 'exo_role', 'status', 'visible',
    )
    list_filter = ('exo_role__categories', 'status', 'visible')
    search_fields = ('project__name', 'user__full_name', 'role__name')


@admin.register(models.ConsultantRoleCertificationGroup)
class ConsultantRoleCertificationGroupAdmin(admin.ModelAdmin):
    list_display = (
        '_type', 'name', 'description', 'created_by', 'issued_on', 'created',
    )
    list_filter = ('_type',)
    search_fields = ('name', 'description')


@admin.register(models.OrganizationUserRole)
class OrganizationUserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'position', 'status', 'created')
    list_filter = ('status', 'visible')


@admin.register(models.HubUser)
class HubUserAdmin(admin.ModelAdmin):
    search_fields = ('user__full_name', 'user__email',)
    list_display = ('user', 'hub',)
    list_filter = ('hub',)


admin.site.register(models.CustomerUserRole)
admin.site.register(models.PartnerProjectRole)
admin.site.register(models.PartnerUserRole)
