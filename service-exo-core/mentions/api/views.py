from django.conf import settings

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from actstream.models import Follow

from circles.models import Circle
from custom_auth.helpers import UserProfileWrapper

from .serializers import SearchMentionSerializer, UserMentionResultsSerializer


class SearchMentionAPIView(GenericAPIView):

    permission_classes = (IsAuthenticated, )
    serializer_class = SearchMentionSerializer
    output_serializer_class = UserMentionResultsSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            search = serializer.data.get('search').lower()
            circle = Circle.objects.get(pk=serializer.data.get('circle_pk'))
            followers = Follow.objects.followers_qs(
                circle).filter(user__full_name__icontains=search)[:5]
            results = [
                {'type_object': 'user',
                 'name': follow.user.full_name,
                 'uuid': follow.user.pk,
                 'url': settings.DOMAIN_NAME + UserProfileWrapper(follow.user).profile_public_slug_url}
                for follow in followers
            ]
            output_serializer = self.output_serializer_class(
                data=results, many=True)
            if output_serializer.is_valid():
                data = output_serializer.data
                status_code = status.HTTP_200_OK
            else:
                data = output_serializer.errors
                status_code = status.HTTP_400_BAD_REQUEST

            response = Response(
                data=data,
                status=status_code,
            )

        else:
            response = Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

        return response
