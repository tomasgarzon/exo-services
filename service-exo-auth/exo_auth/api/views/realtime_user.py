import jwt

from rest_framework import views, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model
from django.conf import settings

from ..serializers.subscription import (
    UserSubscriptionSerializer,
    SubscribeSerializer,
    UnsubscribeSerializer)
from ...models import UserSubscription


class UserJWTView(views.APIView):
    model = get_user_model()

    def post(self, request, format=None):
        ticket = request.data.get('ticket', None)
        if not ticket:
            raise ticket
        options = {
            'verify_exp': settings.JWT_AUTH['JWT_VERIFY_EXPIRATION'],
        }

        user_data = jwt.decode(
            ticket,
            settings.JWT_SECRET_KEY,
            True,
            options=options,
            leeway=0,
            audience=None,
            issuer=None,
            algorithms=['HS256']
        )
        user_data['status'] = 'ok'
        return Response(user_data)


class OnSubscribeView(generics.CreateAPIView):
    model = UserSubscription
    serializer_class = SubscribeSerializer


class OnUnsubscribeView(generics.CreateAPIView):
    model = UserSubscription
    serializer_class = UnsubscribeSerializer


class UserSubscribeView(generics.ListAPIView):
    serializer_class = UserSubscriptionSerializer
    model = UserSubscription
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        subscription = self.kwargs.get('subscription')
        return UserSubscription.objects.filter(subscription=subscription)
