from django.contrib import admin  # noqa

# Register your models here.
from . import models


class KeywordAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'created_by', 'public',
    )
    list_filter = ('public', )
    search_fields = ('name', 'created_by__short_name')


admin.site.register(models.Keyword, KeywordAdmin)
