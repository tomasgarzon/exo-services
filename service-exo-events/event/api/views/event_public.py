from django.utils import timezone

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter as RestFrameworkSearchFilter
from rest_framework import generics

from ...models import Event
from ..serializers.event_detail_public import (
    EventDetailPublicWebsiteSerializer,
    EventPublicSerializer)
from ..filters import EventFilterSet
from .custom_pagination import StandardResultsSetPagination


class PublicEventSearchViewSet(generics.ListAPIView):

    model = Event
    serializer_class = EventDetailPublicWebsiteSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (RestFrameworkSearchFilter, DjangoFilterBackend)
    search_fields = ('title', 'created_by_full_name')
    filter_class = EventFilterSet

    def get_queryset(self):
        queryset = self.model.public_objects.filter(
            start__gte=timezone.now().date()
        ).distinct()
        return queryset.order_by('start')


class PublicEventView(generics.RetrieveAPIView):
    model = Event
    lookup_field = 'uuid'
    lookup_url_kwarg = 'event_id'
    serializer_class = EventPublicSerializer
    queryset = Event.objects.all()
