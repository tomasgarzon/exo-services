from rest_framework import serializers

from django.conf import settings
from django.contrib.auth import get_user_model

from actstream import action

from utils.mail import handlers
from custom_auth.helpers import UserProfileWrapper


class RequestContactSerializer(serializers.Serializer):

    comment = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True)

    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.filter(
            is_active=True))

    def create(self, validated_data):
        user_from = self.context.get('user_from')
        user_to = validated_data.get('user')
        data = {
            'verb': settings.USER_PROFILE_ACTION_REQUEST_CONTACT,
            'action_object': user_to,
            'description': validated_data.get('comment'),
        }
        action.send(
            user_from,
            **data
        )
        handlers.mail_handler.send_mail(
            'request_user_contact',
            recipients=[user_to.email],
            short_name=user_to.short_name,
            requester_name=user_from.get_full_name(),
            requester_short_name=user_from.short_name,
            requester_email=user_from.email,
            user_title=user_from.user_title,
            requester_profile_picture=user_from.profile_picture.get_thumbnail_url(),
            requester_profile_url=UserProfileWrapper(user_from).profile_slug_url,
            comment=validated_data.get('comment'),
        )
        return validated_data
