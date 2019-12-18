from django.contrib import admin    # NOQA

# Register your models here.
from .import models


class AssignmentStepAdmin(admin.ModelAdmin):
    list_filter = ('step__project', 'streams')
    list_display = (
        'project', 'step', 'name',
        'order', 'streams_display', 'created_by')

    def streams_display(self, obj):
        return ', '.join(obj.streams.all())


class InformationBlockAdmin(admin.ModelAdmin):
    list_filter = ('type',)
    list_display = (
        'pk', 'type', 'content_type', 'content_object',
        'title', 'subtitle', 'order', 'created_by')


class AssignmentTextAdmin(admin.ModelAdmin):
    list_display = (
        'block', 'text', 'created_by')


class AssignmentAdviceItemAdmin(admin.ModelAdmin):
    list_display = (
        'assignment_advice', 'description',
        'order', 'created_by')


class AssignmentTaskItemAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'project', 'step', 'assignment_task',
        'name', 'order', 'created_by')


class AssignmentStepTeamAdmin(admin.ModelAdmin):
    list_filter = ('team',)
    list_display = (
        'project', 'assignment_step',
        'team', 'stream_display', 'created_by')

    def stream_display(self, obj):
        return obj.team.get_stream_display()


class AssignmentTaskTeamAdmin(admin.ModelAdmin):
    list_display = (
        'assignment_step_team', 'assignment_task_item',
        'status', 'team', 'created_by')


class AssignmentResourceAdmin(admin.ModelAdmin):
    list_display = ('block',)


class AssignmentResourceItemAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'type', 'link')


admin.site.register(models.AssignmentAdvice)
admin.site.register(models.AssignmentAdviceItem, AssignmentAdviceItemAdmin)
admin.site.register(models.AssignmentResource, AssignmentResourceAdmin)
admin.site.register(models.AssignmentResourceItem, AssignmentResourceItemAdmin)
admin.site.register(models.AssignmentStep, AssignmentStepAdmin)
admin.site.register(models.AssignmentStepTeam, AssignmentStepTeamAdmin)
admin.site.register(models.AssignmentTask)
admin.site.register(models.AssignmentTaskItem, AssignmentTaskItemAdmin)
admin.site.register(models.AssignmentTaskTeam, AssignmentTaskTeamAdmin)
admin.site.register(models.AssignmentText, AssignmentTextAdmin)
admin.site.register(models.InformationBlock, InformationBlockAdmin)
