from graphene import AbstractType
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
from graphene_django import DjangoObjectType
import graphene
from graphene.types.json import JSONString

from .filter import InvitationFilter
from ..models import Invitation
from .invitation_mixin import InvitationMixin


class PublicInvitationNode(InvitationMixin, DjangoObjectType):
    extra_data = JSONString()
    inv_status = graphene.String()
    inv_type = graphene.String()

    class Meta:
        model = Invitation
        interfaces = (relay.Node, )
        only_fields = ['hash', 'inv_status', 'inv_type']


class PublicQuery(AbstractType):
    all_invitation = DjangoFilterConnectionField(
        PublicInvitationNode,
        filterset_class=InvitationFilter,
    )
