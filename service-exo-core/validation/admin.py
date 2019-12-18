from django.contrib import admin

from . import models
# Register your models here.


class ValidationAdmin(admin.ModelAdmin):
    list_filter = ('status', 'validation_type', 'validation_detail')
    list_display = ('subject', 'validation_detail', 'validation_type', 'status', 'message', 'project')


admin.site.register(models.Validation, ValidationAdmin)
