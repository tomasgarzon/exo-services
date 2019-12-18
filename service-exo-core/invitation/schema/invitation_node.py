from graphene_django import DjangoObjectType
from graphene.types.json import JSONString
import graphene

from utils.schema import CustomNode

from ..models import Invitation, InvitationObject
from .invitation_mixin import InvitationMixin


class InvitationNode(InvitationMixin, DjangoObjectType):
    extra_data = JSONString()
    inv_status = graphene.String()
    inv_type = graphene.String()

    class Meta:
        model = Invitation
        interfaces = (CustomNode, )
        exclude_fields = ['status', 'type']


class InvitationObjectNode(DjangoObjectType):

    class Meta:
        model = InvitationObject
        interfaces = (CustomNode, )
