from rest_framework import serializers

from exo_accounts.models import EmailAddress

from ...models import Invitation


class ResendInvitationUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    invitation = serializers.PrimaryKeyRelatedField(queryset=Invitation.objects.all())

    def validate(self, data):
        email = data.get('email')
        user = data.get('invitation').user
        if EmailAddress.objects.filter(email=email).exclude(user=user).exists():
            raise serializers.ValidationError('This email is already being used')
        return data

    def create(self, validated_data):
        invitation = validated_data.get('invitation')
        user = invitation.user
        user.email = validated_data.get('email')
        user.save()
        return user
