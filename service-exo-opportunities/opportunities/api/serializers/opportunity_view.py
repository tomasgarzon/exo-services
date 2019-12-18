from rest_framework import serializers

from django.conf import settings

from ...models import Opportunity


class OpportunitySerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    chat_url = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = ['uuid', 'title', 'url', 'chat_url']
        ref_name = 'OpportunityURLChatSerializer'

    def get_url(self, obj):
        if obj.created_by == self.context.get('request').user:
            return obj.admin_url_public
        return obj.url_public

    def get_chat_url(self, obj):
        user = self.context.get('request').user
        user_is_manager = obj.group and user in obj.group.managers.all()
        if obj.created_by == user or user_is_manager:
            return obj.admin_url_public
        return settings.OPPORTUNITIES_CHAT_URL.format(obj.pk)
