import graphene

from django.shortcuts import get_object_or_404

from graphene_django import DjangoObjectType

from team.models import Team
from utils.schema import CustomNode

from ..models import MicroLearning
from .user_microlearning import UserMicroLearningNode


class MicroLearningNode(DjangoObjectType):
    user = graphene.Field(UserMicroLearningNode)

    class Meta:
        model = MicroLearning
        interfaces = (CustomNode, )

    def resolve_user(self, info):
        team = get_object_or_404(
            Team,
            **{'pk': info.variable_values.get('pkTeam'),
               'project_id': info.variable_values.get('pk')
               })
        user_microlearning = None
        if self.user_can_fill(info.context.user):
            user_microlearning, _ = self.responses.get_or_create(
                user=info.context.user,
                team=team,
            )
        return user_microlearning
