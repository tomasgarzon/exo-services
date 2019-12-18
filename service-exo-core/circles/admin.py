from django.contrib import admin

from .models import Circle


@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    list_filter = ('hub', 'type')
    list_display = ('name', 'hub', 'code', 'type', 'description')
