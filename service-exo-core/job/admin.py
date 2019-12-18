from django.contrib import admin

from .models import CoreJob


@admin.register(CoreJob)
class CoreJobAdmin(admin.ModelAdmin):
    list_filter = ('content_type',)
    list_display = (
        'uuid',
        'content_object',
        'content_type',
        'object_id',
        'created',
    )
