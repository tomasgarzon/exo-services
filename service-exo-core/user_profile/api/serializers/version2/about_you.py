from django.contrib.auth import get_user_model

from rest_framework import serializers


class AboutYouSerializer(serializers.ModelSerializer):
    skype = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    website = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    facebook = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    linkedin = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    twitter = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    class Meta:
        model = get_user_model()
        fields = [
            'skype',
            'website',
            'linkedin',
            'twitter',
            'facebook',
            'phone',
            'bio_me'
        ]

    def __init__(self, instance, *args, **kwargs):
        instance.initialize_social_networks()
        super().__init__(instance, *args, **kwargs)
