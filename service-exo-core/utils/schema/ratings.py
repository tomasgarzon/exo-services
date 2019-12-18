import graphene
import django_filters
from graphene_django import DjangoObjectType

from ratings.models import Rating, OverallRating

from .node import CustomNode


class RatingFilterSet(django_filters.FilterSet):
    pk = django_filters.CharFilter()

    class Meta:
        model = Rating
        fields = ['pk']


class OverallRatingFilterSet(django_filters.FilterSet):
    pk = django_filters.CharFilter()

    class Meta:
        model = OverallRating
        fields = ['pk']


class RatingNode(DjangoObjectType):

    class Meta:
        model = Rating
        interfaces = (CustomNode,)


class OverallRatingNode(DjangoObjectType):

    user_status = graphene.String()

    class Meta:
        model = OverallRating
        interfaces = (CustomNode,)

    def resolve_user_status(self, info):
        user = info.context.user
        return self.user_status(user)
