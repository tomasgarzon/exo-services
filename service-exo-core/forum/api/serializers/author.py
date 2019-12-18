from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import serializers

from custom_auth.helpers import UserProfileWrapper
from project.user_title_helpers import get_user_title_in_project
from user_profile.api.serializers.profile_picture import UserProfilePictureSerializer


class ForumAuthorSerializer(serializers.ModelSerializer):
    profile_pictures = UserProfilePictureSerializer(many=True)
    profile_url = serializers.SerializerMethodField()
    project_title = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            'pk',
            'short_name',
            'full_name',
            'project_title',
            'user_title',
            'slug',
            'profile_pictures',
            'profile_url',
            'uuid',
        ]

    def get_project_title(self, instance):
        project = self.context.get('project', None)
        if project:
            return get_user_title_in_project(user=instance, project=project)
        else:
            return ''

    def get_profile_url(self, instance):
        return settings.DOMAIN_NAME + UserProfileWrapper(instance).profile_public_slug_url
