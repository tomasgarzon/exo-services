from graphene_django import DjangoObjectType
import graphene

from utils.schema import CustomNode
from consultant.helpers.cache import (
    KeywordFieldFilled,
    ProfilePictureFieldFilled,
    SummaryFieldFilled
)

from ..models import Achievement, UserAchievement


class AchievementNode(DjangoObjectType):

    class Meta:
        model = Achievement
        interfaces = (CustomNode, )


class UserAchievementNode(DjangoObjectType):
    keywords = graphene.Boolean()
    profile_picture = graphene.Boolean()
    about_me = graphene.Boolean()

    class Meta:
        model = UserAchievement
        interfaces = (CustomNode, )

    def resolve_keywords(self, info):
        if not self.user.is_consultant:
            return None
        return KeywordFieldFilled(self.user.consultant).check()

    def resolve_profile_picture(self, info):
        if not self.user.is_consultant:
            return None
        return ProfilePictureFieldFilled(self.user.consultant).check()

    def resolve_about_me(self, info):
        if not self.user.is_consultant:
            return None
        return SummaryFieldFilled(self.user.consultant).check()
