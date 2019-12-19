from django.contrib import admin

# Register your models here.
from .models import Post, Answer


class PostAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_filter = ('status', '_type')
    list_display = ('title', 'status', '_type', 'content_type', 'object_id', 'created_by', 'created')


class AnswerAdmin(admin.ModelAdmin):
    search_fields = ('post__title', 'comment')
    list_filter = ('status',)
    list_display = ('post', 'comment', 'status', 'created_by', 'created')


admin.site.register(Post, PostAdmin)
admin.site.register(Answer, AnswerAdmin)
