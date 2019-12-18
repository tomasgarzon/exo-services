from graphene import AbstractType
from graphene_django.filter import DjangoFilterConnectionField

from .filter import InvitationFilter
from .invitation_node import InvitationNode


class Query(AbstractType):
    all_invitation = DjangoFilterConnectionField(
        InvitationNode,
        filterset_class=InvitationFilter,
    )
