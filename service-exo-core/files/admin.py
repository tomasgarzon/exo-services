from django.contrib import admin

from . import models


class UploadedFileAdmin(admin.ModelAdmin):
    list_display = (
        'filename', 'mimetype', 'filename_slug',
        'content_type', 'object_id', 'related',
        'created_by', 'created'
    )


class UploadedFileVersionAdmin(admin.ModelAdmin):
    list_filter = ('filestack_status', )
    list_display = (
        'uploaded_file', 'version',
        'filestack_url', 'filestack_status',
        'created_by', 'created'
    )


class UploadedFileVisibilityAdmin(admin.ModelAdmin):
    list_filter = ('visibility', )
    list_display = (
        'uploaded_file', 'visibility',
        'content_type', 'object_id', 'related',
        'created_by', 'created'
    )


admin.site.register(models.Resource)
admin.site.register(models.UploadedFile, UploadedFileAdmin)
admin.site.register(models.UploadedFileVersion, UploadedFileVersionAdmin)
admin.site.register(models.UploadedFileVisibility, UploadedFileVisibilityAdmin)
