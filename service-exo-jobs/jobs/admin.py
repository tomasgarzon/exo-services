from django.contrib import admin

# Register your models here.
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_filter = ('category', 'status')
    list_display = (
        'uuid',
        'category', 'exo_role',
        'status', 'status_detail',
        'title', 'url',
        'start', 'end',
        'extra_data', 'created',
    )
