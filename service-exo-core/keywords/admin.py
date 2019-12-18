from django.contrib import admin  # noqa

# Register your models here.
from . import models


class KeywordAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'created_by', 'public', 'get_tags',
    )
    list_filter = ('public', )
    search_fields = ('name', 'created_by__short_name')

    def get_tags(self, obj):
        tags = obj.tags.all().values_list('name', flat=True)
        return '/'.join([str(i) for i in tags])


admin.site.register(models.Keyword, KeywordAdmin)
