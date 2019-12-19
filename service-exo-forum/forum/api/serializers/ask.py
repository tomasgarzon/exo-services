from rest_framework import serializers

from files.api.serializers.mixins import FilesCreationSerializerMixin
from keywords.api.serializers.keyword import KeywordSerializer
from keywords.api.serializers.keyword_mixin import KeywordSerializerMixin
from team.models import Team

from .post import PostDetailSerializer
from ...models import Post


class TeamQuestionSerializerMixin(
        KeywordSerializerMixin,
        serializers.ModelSerializer,
):
    tags = KeywordSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ['title', 'description', 'tags', 'team', 'pk']

    def create_post(self, validated_data, **kwargs):
        raise NotImplementedError

    def create(self, validated_data):
        user = self.context['request'].user
        team_pk = self.context['view'].kwargs.get('team_pk')
        team = Team.objects.get(pk=team_pk)
        user_can_write = team.check_user_can_post(user)
        if not user_can_write:
            raise serializers.ValidationError(
                'User cannot create questions within this project/team')

        tags = self.sync_tags(
            tags=validated_data.get('tags'),
            user=self.context.get('request').user,
        )
        data_for_creating_post = {
            'title': validated_data.get('title'),
            'description': validated_data.get('description'),
            'tags': tags,
            'team': team,
        }

        return self.create_post(
            validated_data,
            **data_for_creating_post)


class AskTheEcosystemSerializer(
        FilesCreationSerializerMixin,
        TeamQuestionSerializerMixin):

    def create_post(self, validated_data, **kwargs):
        user = self.context.get('request').user
        post = self.Meta.model.objects.create_project_team_post(
            user_from=user, **kwargs)
        self.save_files(user_from=user, instance=post)
        return post

    def to_representation(self, obj):
        context = {'request': self.context.get('request')}
        return PostDetailSerializer(obj, context=context).data
