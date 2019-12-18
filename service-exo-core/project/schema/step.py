from graphene_django import DjangoObjectType
import graphene
from graphene_django.filter import DjangoFilterConnectionField

from utils.schema import CustomNode
from utils.schema import (
    GenericTypeformFeedbackNode,
    SimplyUserGenericTypeformFeedbackNode,
    GenericTypeformFeedbackFilterSet)
from utils.typeform_feedback import build_simple_user_feedback
from learning.schema import MicrolearningAverageNode
from learning.models.microlearning_average import MicroLearningAverage
from team.models import Team

from ..models import Step, StepStream


class StepStreamNode(DjangoObjectType):

    guidelines = graphene.String()
    typeform_feedback = DjangoFilterConnectionField(
        GenericTypeformFeedbackNode,
        filterset_class=GenericTypeformFeedbackFilterSet)
    user_typeform_feedback = graphene.Field(SimplyUserGenericTypeformFeedbackNode)
    microlearning_average = graphene.Field(
        MicrolearningAverageNode,
    )

    class Meta:
        model = StepStream
        interfaces = (CustomNode, )

    def resolve_guidelines(self, info):
        return self.guidelines

    def resolve_user_typeform_feedback(self, info):
        return build_simple_user_feedback(info.context.user, self)

    def resolve_microlearning_average(self, info):
        pkTeam = info.variable_values.get('pkTeam')
        if not pkTeam:
            return None
        team = Team.objects.get(pk=pkTeam)
        return MicroLearningAverage(self, info.context.user, team)


class StepNode(DjangoObjectType):

    class Meta:
        model = Step
        interfaces = (CustomNode, )
