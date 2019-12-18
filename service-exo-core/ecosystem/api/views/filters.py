from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.drf.permissions import ConsultantPermission

from ..serializers.filters import EcosystemFilterSerializer
from ...helpers import filters


class EcosystemFiltersAPIView(APIView):
    permission_classes = (IsAuthenticated, ConsultantPermission)
    serializer_class = EcosystemFilterSerializer

    def get(self, request, format=None):

        data_filters = [
            filters.get_industries_filter_data(),
            filters.get_attributes_filter_data(),
            filters.get_roles_filter_data(),
            filters.get_activities_filter_data(),
            filters.get_technologies_filter_data(),
            filters.get_languages_filter_data(),
            filters.get_location_filter_data(),
            filters.get_certifications_filter_data(),
        ]

        if request.user.is_staff:
            data_filters.append(filters.get_staff_filter_data())

        serializer = self.serializer_class(data_filters, many=True)

        return Response(serializer.data)
