from django.contrib import admin

from . import models


class MicroLearningAdmin(admin.ModelAdmin):
    list_display = (
        'step_stream',
        'typeform_url',
        'description',
        'created',
    )


class UserMicroLearningAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'microlearning',
        'team',
        'score',
        'status',
    )


admin.site.register(models.MicroLearning, MicroLearningAdmin)
admin.site.register(models.UserMicroLearning, UserMicroLearningAdmin)
