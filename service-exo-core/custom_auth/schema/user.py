from django.contrib.auth import get_user_model
from django.conf import settings

import django_filters
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
import graphene
from graphene import AbstractType

from user_profile.schema import CertificationCredentialNode
from utils.schema import CustomNode

from .email_address import EmailAddressNode, EmailAddressFilterSet
from .social_network import SocialNetworkNode, SocialNetworkFilterSet
from ..helpers import UserProfileWrapper


class UserProfilePictureNode(graphene.ObjectType):
    width = graphene.Int()
    height = graphene.Int()
    url = graphene.String()


class UserNode(DjangoObjectType):
    emailaddress = DjangoFilterConnectionField(
        EmailAddressNode,
        filterset_class=EmailAddressFilterSet)
    profile_pictures = graphene.List(UserProfilePictureNode)
    is_consultant = graphene.Boolean()
    social_networks = DjangoFilterConnectionField(
        SocialNetworkNode,
        filterset_class=SocialNetworkFilterSet)
    timezone = graphene.String()
    certificates = graphene.List(CertificationCredentialNode)
    is_openexo_member = graphene.Boolean()
    user_title = graphene.String()

    class Meta:
        model = get_user_model()
        interfaces = (CustomNode, )
        exclude_fields = ['password', 'profile_picture']

    def resolve_emailaddress(self, info):
        return self.emailaddress_set.all()

    def resolve_profile_pictures(self, info):
        return self.profile_pictures

    def resolve_social_networks(self, info):
        self.initialize_social_networks()
        social_networks = []
        for _, name in settings.EXO_ACCOUNTS_CH_SOCIAL_NETWORK:
            social = getattr(self, name.lower())
            if social.value:
                social_networks.append(social)
        return social_networks

    def resolve_timezone(self, info):
        return self.timezone.zone if self.timezone else None

    def resolve_certificates(self, info):
        return self.consultant.get_certificates() if self.is_consultant else []

    def resolve_is_openexo_member(self, info):
        user_wrapper = UserProfileWrapper(self)
        return user_wrapper.is_openexo_member

    def resolve_user_title(self, info):
        return self.user_title


class UserFilter(django_filters.FilterSet):
    pk = django_filters.CharFilter()

    class Meta:
        model = get_user_model()
        fields = ['pk']


class Query(AbstractType):
    user = CustomNode.Field(UserNode)
    all_users = DjangoFilterConnectionField(
        UserNode,
        filterset_class=UserFilter)
