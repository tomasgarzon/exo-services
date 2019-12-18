from graphene_django import DjangoObjectType

from utils.schema import CustomNode

from ..models import Reward, UserReward


class RewardNode(DjangoObjectType):

    class Meta:
        model = Reward
        interfaces = (CustomNode, )


class UserRewardNode(DjangoObjectType):

    class Meta:
        model = UserReward
        interfaces = (CustomNode, )
