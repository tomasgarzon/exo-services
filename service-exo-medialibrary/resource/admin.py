from django.contrib import admin
from django.utils.html import format_html
from admin_actions.admin import ActionsModelAdmin

from .models import Category, Tag, Resource
from .views.upload_file import UploadFileView


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'num_tags', 'created', 'modified')

    def num_tags(self, obj):
        return obj.tags.count()


class TagAdmin(admin.ModelAdmin):
    list_filter = ('category', 'default_show_filter')
    list_display = ('name', 'slug', 'category', 'created', 'modified', 'default_show_filter')


class ResourceAdmin(ActionsModelAdmin):
    list_filter = ('status', 'type')
    list_display = ('name', 'type', 'status',
                    'link', 'current_tags',
                    'sections', 'projects', 'created',
                    'preview', 'iframe', )
    actions_list = ('custom_list_action', )

    def custom_list_action(self, request):
        view = UploadFileView.as_view()
        return view(request)
    custom_list_action.short_description = 'Upload file to filestack'
    custom_list_action.url_path = 'upload-file-to-filestack'

    def current_tags(self, obj):
        data = ''
        for tag in obj.tags.all():
            data += tag.name + ", "
        return data[:-2]

    def preview(self, obj):
        thumbnail = None
        if obj.thumbnail:
            iframe_formated = '<img width="150" height="100" src="{}" alt="Thumbnail">'.format(obj.thumbnail)
            thumbnail = format_html(iframe_formated)
        return thumbnail

    def iframe(self, obj):
        iframe_formated = '<div style=width:200px;height:200px>{}</div>'.format(obj.get_video_iframe())
        return format_html(iframe_formated)


admin.site.register(Resource, ResourceAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
