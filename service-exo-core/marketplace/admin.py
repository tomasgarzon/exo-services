from django.contrib import admin

from .models import ServiceRequest


class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'email', 'status',
        'participant', 'motivation', 'goal',
        'employees', 'initiatives', 'book',
    )
    list_filter = ('status',)
    search_fields = ('email',)


admin.site.register(ServiceRequest, ServiceRequestAdmin)
