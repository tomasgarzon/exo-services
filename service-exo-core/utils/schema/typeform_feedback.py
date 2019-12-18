import graphene
import django_filters
from django.contrib.contenttypes.models import ContentType

from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from typeform_feedback.models import GenericTypeformFeedback, UserGenericTypeformFeedback
from utils.schema import CustomNode


class UserGenericTypeformFeedbackFilterSet(django_filters.FilterSet):
    pk = django_filters.CharFilter()

    class Meta:
        model = UserGenericTypeformFeedback
        fields = ['pk']


class UserGenericTypeformFeedbackNode(DjangoObjectType):

    url = graphene.String()

    class Meta:
        model = UserGenericTypeformFeedback
        interfaces = (CustomNode, )

    def resolve_url(self, info):
        return self.feedback.typeform_url


class GenericTypeformFeedbackFilterSet(django_filters.FilterSet):
    pk = django_filters.CharFilter()

    class Meta:
        model = GenericTypeformFeedback
        fields = ['pk']


class GenericTypeformFeedbackNode(DjangoObjectType):

    typeform_url = graphene.String()
    responses = DjangoFilterConnectionField(
        UserGenericTypeformFeedbackNode,
        filterset_class=UserGenericTypeformFeedbackFilterSet)

    class Meta:
        model = GenericTypeformFeedback
        interfaces = (CustomNode, )

    def resolve_typeform_url(self, info):
        return self.url

    def resolve_responses(self, info):
        return self.responses.filter(user=info.context.user)


class SimplyUserGenericTypeformFeedbackNode(graphene.ObjectType):
    user_feedback_id = graphene.Int()
    url = graphene.String()
    status = graphene.String()

    class Meta:
        interfaces = (CustomNode, )

    def resolve_content_type_id(self, info):
        return ContentType.objects.get_for_model(self.object).pk

    def resolve_content_type(self, info):
        return [ContentType.objects.get_for_model(self.object)]

    def resolve_user_feedback_id(self, info):
        return self.pk
