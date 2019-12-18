from django.contrib.auth import get_user_model

from rest_framework import serializers

from ...helpers.cache import (
    KeywordFieldFilled,
    ProfilePictureFieldFilled,
    SummaryFieldFilled
)


class RequirementSerializer(serializers.ModelSerializer):
    keywords = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    about_me = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['keywords', 'profile_picture', 'about_me']

    def get_keywords(self, obj):
        if not obj.is_consultant:
            return None
        return KeywordFieldFilled(obj.consultant).check()

    def get_profile_picture(self, obj):
        if not obj.is_consultant:
            return None
        return ProfilePictureFieldFilled(obj.consultant).check()

    def get_about_me(self, obj):
        if not obj.is_consultant:
            return None
        return SummaryFieldFilled(obj.consultant).check()
