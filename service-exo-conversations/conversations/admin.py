from django.contrib import admin

from .models import Conversation, ConversationUser, Message
from .forms import ConversationUserForm


class ConversationUserInline(admin.TabularInline):
    model = ConversationUser
    exclude = [
        'user'
    ]
    form = ConversationUserForm


class ConversationAdmin(admin.ModelAdmin):
    list_display = ('name', 'type_display', 'uuid_related_object', 'uuid')
    list_filter = ('_type', )
    readonly_fields = ('uuid',)
    search_fields = ['name', 'uuid_related_object', 'users__user__uuid']
    exclude = ['created_by']
    inlines = [
        ConversationUserInline
    ]

    def type_display(self, obj):
        return obj.get__type_display()
    type_display.short_description = 'Type'

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.conversation.remove_user(obj.user)
            obj.delete()
        for form in formset.forms:
            form.save()
        formset.save_m2m()


admin.site.register(Conversation, ConversationAdmin)


class MessageAdmin(admin.ModelAdmin):
    list_display = ('message', 'conversation_name', 'created_by',)
    search_fields = ['message', 'conversation__uuid_related_object', 'created_by__uuid']
    exclude = ['created_by']

    def conversation_name(self, obj):
        return obj.conversation.name
    conversation_name.short_description = 'Conversation'


admin.site.register(Message, MessageAdmin)
