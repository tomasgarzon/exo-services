from django.contrib.auth import get_user_model

from rest_framework import serializers


class ProfileSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = [
            'bio_me',
            'about_me',
        ]
