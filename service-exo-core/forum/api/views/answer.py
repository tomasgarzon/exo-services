from django.core.exceptions import PermissionDenied

from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from utils.drf.parsers import CamelCaseJSONParser
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.exceptions import ValidationError
from guardian.mixins import PermissionRequiredMixin as GuardianPermissionRequiredMixin

from ...models import Answer
from ..serializers.answer import AnswerSerializer, AnswerCreateUpdateSerializer
from ..serializers import actions
from ..serializers.answer import AnswerPostSerializer
from ...conf import settings


class AnswerViewSet(
        GuardianPermissionRequiredMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    """
    API REST for answer management that provides these actions:

    `update`, `destroy`, `up-vote`, `down-vote`

    update:
    Update an answwr instance.

    destroy:
    Destroy an answer instance.

    down-vote
    Post vote down

    up-vote
    Post vote up
    """
    return_404 = True
    queryset = Answer.objects.all()
    renderer_classes = (CamelCaseJSONRenderer, )
    parser_classes = (CamelCaseJSONParser,)
    serializers = {
        'default': AnswerSerializer,
        'update': AnswerCreateUpdateSerializer,
        'rating': actions.RatingSerializer,
    }

    custom_permissions = {
        'update': settings.FORUM_PERMS_EDIT_ANSWER,
        'destroy': settings.FORUM_PERMS_EDIT_ANSWER,
        'like': 'can_vote',
        'rating': 'can_rate',
    }

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    def perform_destroy(self, instance):
        instance.mark_as_removed(self.request.user)

    def check_permissions(self, request):
        if request.user.is_anonymous:
            raise PermissionDenied()
        forbidden = False
        # we have to do this, because self.action is filled after this code
        method = request.method.lower()
        if method == 'options':
            self.action = 'metadata'
        else:
            self.action = self.action_map.get(method)
        permission_name = self.custom_permissions.get(self.action)
        if not permission_name:
            # operation without permissions, each method has to check manually
            return None
        else:
            try:
                self.get_object()
            except AssertionError:  # DRF Openapi error
                return False
            if hasattr(self.get_object(), permission_name):
                forbidden = not getattr(self.get_object(), permission_name)(
                    request.user, raise_exceptions=False)
            else:
                forbidden = not request.user.has_perm(permission_name, self.get_object())
        if forbidden:
            raise PermissionDenied()

    def perform_update(self, serializer):
        serializer.save(user_from=self.request.user)

    @action(detail=True, methods=['put'], url_path='rating')
    def rating(self, request, pk):
        answer = self.get_object()
        if not answer.can_rate(request.user, raise_exceptions=False):
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: ["User can't rate the answer"],
            })
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user_from=request.user, answer=answer)
        serializer = AnswerPostSerializer(
            answer, context={'request': self.request})
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='like')
    def like(self, request, pk):
        instance = self.get_object()
        if not instance.can_vote(request.user, raise_exceptions=False):
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: ["User can't vote the answer"],
            })
        if not instance.have_liked(request.user):
            instance.do_like(request.user)
        serializer = AnswerPostSerializer(
            instance, context={'request': self.request})
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='unlike')
    def unlike(self, request, pk):
        instance = self.get_object()
        if not instance.can_vote(request.user, raise_exceptions=False):
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: ["User can't vote the answer"],
            })
        if instance.have_liked(request.user):
            instance.clear_previous_votes(request.user)
        serializer = AnswerPostSerializer(
            instance, context={'request': self.request})
        return Response(serializer.data)
