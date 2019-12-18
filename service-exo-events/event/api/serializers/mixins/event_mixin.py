from django.conf import settings

from rest_framework import serializers

from ....models import Event


class EventMixinSerializer(serializers.ModelSerializer):

    follow_type = serializers.ChoiceField(choices=settings.EVENT_FOLLOW_MODE_CHOICES, required=False)
    follow_type_name = serializers.SerializerMethodField(read_only=True)
    trainer = serializers.SerializerMethodField()
    event_image = serializers.CharField(source='url_image', required=False, allow_blank=True)

    class Meta:
        model = Event

    def get_follow_type_name(self, obj):
        return obj.get_follow_type_display()

    def get_trainer(self, obj):
        user_data = obj.main_speaker_data
        return {
            'username': user_data.get('fullName'),
            'email': user_data.get('email'),
            'profile_url': user_data.get('profileUrl'),
            'picture': user_data.get('profilePicture'),
        }
