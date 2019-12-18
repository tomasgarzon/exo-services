import graphene

from django.conf import settings

from graphene_django import DjangoObjectType

from utils.schema import CustomNode

from ..models import ConsultantProjectRole, UserProjectRole


class ConsultantProjectRoleNode(DjangoObjectType):
    rating = graphene.Float()

    class Meta:
        model = ConsultantProjectRole
        interfaces = (CustomNode, )

    def resolve_rating(self, info):
        if info.context.user.has_perm(settings.EXO_ACCOUNTS_PERMS_USER_EDIT, self.consultant.user):
            return self.rating or 0
        return None


class UserProjectRoleNode(DjangoObjectType):

    class Meta:
        model = UserProjectRole
        interfaces = (CustomNode, )
