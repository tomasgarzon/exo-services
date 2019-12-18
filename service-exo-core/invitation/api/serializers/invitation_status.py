from django.conf import settings

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from invitation.models import Invitation
from frontend.helpers import UserRedirectController


class InvitationAcceptStatusSerializer(serializers.ModelSerializer):

    description = serializers.CharField(required=False)

    class Meta:
        model = Invitation
        fields = ('description',)

    def validate(self, attrs):
        invitation = self.instance
        user = self.context.get('request').user
        invitation.can_be_accepted(user, raise_errors=True)
        return attrs

    def get_next_url(self, obj):
        next_url, _ = UserRedirectController.redirect_url(obj.user)
        obj.user.refresh_from_db()
        if obj.has_registration:
            if obj.has_registration.is_registered:
                next_url = settings.FRONTEND_CIRCLES_PAGE
        return next_url

    def update(self, instance, validated_data):
        instance.accept(**validated_data)
        return instance

    def to_representation(self, obj):
        data = self.initial_data
        data['nextUrl'] = self.get_next_url(obj)
        return data


class InvitationDeclineStatusSerializer(serializers.ModelSerializer):
    declined_message = serializers.CharField(required=False)

    class Meta:
        model = Invitation
        fields = ('declined_message',)

    def validate(self, attrs):
        invitation = self.instance
        user = self.context.get('request').user
        invitation.can_be_cancelled(user, raise_errors=True)
        return attrs

    def get_next_url(self, obj):
        next_url = None
        if obj.has_registration:
            next_url, _ = UserRedirectController.redirect_url(obj.user)
        return next_url

    def update(self, instance, validated_data):
        instance.cancel(
            user=validated_data.get('user'),
            description=validated_data.get('declined_message'),
        )
        return instance

    def to_representation(self, obj):
        data = self.initial_data
        data['nextUrl'] = self.get_next_url(obj)
        return data


class InvitationAcceptAgreementSerializer(InvitationAcceptStatusSerializer):
    pass


class InvitationDeclineAgreementSerializer(InvitationDeclineStatusSerializer):
    pass


class InvitationAcceptProfileSerializer(InvitationAcceptStatusSerializer):
    profile_picture = Base64ImageField(required=False)
    full_name = serializers.CharField()
    short_name = serializers.CharField()
    location = serializers.CharField()
    place_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    personal_mtp = serializers.CharField(
        required=False, allow_blank=True)

    class Meta:
        model = Invitation
        fields = (
            'description',
            'profile_picture',
            'full_name',
            'short_name',
            'location',
            'place_id',
            'personal_mtp',
        )


class InvitationDeclineProfileSerializer(InvitationDeclineStatusSerializer):
    pass
