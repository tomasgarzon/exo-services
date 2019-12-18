from django.contrib import admin

from . import models


@admin.register(models.Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = (
        'id', 'uuid', 'title', 'entity',
        'exo_role', 'certification_required',
        '_status', 'mode',
        'duration_unity', 'duration_value',
        'budget_string', 'location_string',
        'start_date', 'created',
    )
    list_filter = ('_status', 'exo_role', 'duration_unity')


@admin.register(models.Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user_uuid', 'opportunity_title', 'status', 'has_sow', 'created')
    list_filter = ('status', )
    search_fields = ['opportunity__title', 'user__uuid']

    def user_uuid(self, obj):
        return obj.user.uuid.__str__()
    user_uuid.short_description = 'User UUID'

    def opportunity_title(self, obj):
        return obj.opportunity.title
    opportunity_title.short_description = 'Opportunity'


@admin.register(models.ApplicantSow)
class ApplicantSowAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'applicant_name', 'requester_name',
        'mode', 'location', 'entity',
        'start_date', 'end_date', 'start_time', 'timezone',
        'created'
    )
    list_filter = ('mode',)
    search_fields = ['applicant__opportunity__title', 'applicant__user__uuid']


admin.site.register(models.OpportunityGroup)
