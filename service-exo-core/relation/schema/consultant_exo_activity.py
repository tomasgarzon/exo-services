import graphene
import django_filters

from graphene_django import DjangoObjectType

from utils.schema import CustomNode

from ..models import ConsultantActivity


class ConsultantActivityFilterSet(django_filters.FilterSet):
    pk = django_filters.CharFilter()

    class Meta:
        model = ConsultantActivity
        fields = ['pk']


class ConsultantExOActivityNode(DjangoObjectType):

    status = graphene.String()

    class Meta:
        model = ConsultantActivity
        interfaces = (CustomNode, )

    def resolve_user_agreement(self, info):
        return self.consultant_profile.consultant.user.agreements.get(
            agreement=self.exo_activity.agreement_object.agreement,
        )
