from collections import OrderedDict

from rest_framework import viewsets, mixins, exceptions, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination
from rest_framework.settings import api_settings

from django.db.models import Exists, OuterRef, Q
from django.conf import settings

from utils.authentication import UsernameAuthentication

from ...models import Conversation, MessageUser
from ..serializers import conversation as conv_serializers
from ..serializers import message as msg_serializers
from ..serializers import conversation_group


class ConversationViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):

    model = Conversation
    permission_classes = (IsAuthenticated,)
    serializers = {
        'default': conv_serializers.ConversationSerializer,
        'messages': msg_serializers.MessageSerializer,
        'reply': msg_serializers.CreateMessageSerializer,
        'create_group': conversation_group.CreateGroupConversationSerializer,
        'create_message': msg_serializers.CreateMessageFromServiceSerializer,
        'update_conversation': conversation_group.UpdateGroupConversationSerializer
    }
    MESSAGES_page_size = 5
    MESSAGES_cursor_query_param = 'cursor'

    @property
    def related_uuid(self):
        return self.kwargs.get('related_uuid')

    @property
    def authentication_classes(self):
        action = self.action_map.get(self.request.method.lower())
        if action in ['create_message']:
            return [UsernameAuthentication]
        else:
            return api_settings.DEFAULT_AUTHENTICATION_CLASSES

    def get_queryset(self):
        created_by_you = self.request.GET.get('created_by_you', False)
        related_uuid = self.related_uuid
        query2 = Q()
        if related_uuid is not None:
            query = Q(
                uuid_related_object=related_uuid,
                users__user=self.request.user)
        else:
            query = Q(
                _type=settings.CONVERSATIONS_CH_USER,
                users__user=self.request.user)
        if self.request.GET.get('user_to'):
            query2 = Q(
                users__user__uuid=self.request.GET.get('user_to'))
        queryset = Conversation.objects.filter(query).filter(query2)
        if created_by_you:
            queryset = queryset.filter(created_by=self.request.user)
        return queryset.distinct()

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    @action(detail=True, methods=['get'], url_path='messages')
    def messages(self, request, **kwargs):
        conversation = self.get_object()
        seen = MessageUser.objects.filter(
            message=OuterRef('pk'),
            user=request.user)
        queryset = conversation.messages.all(
        ).annotate(user_seen=Exists(seen)).order_by('user_seen', '-created')
        paginator = CursorPagination()
        page_size = conversation.total_unread(request.user)
        if page_size < self.MESSAGES_page_size:
            page_size = self.MESSAGES_page_size
        paginator.page_size = page_size + 3
        paginator.cursor_query_param = 'cursor'

        response = {}
        page = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(
            page, many=True)
        data = serializer.data
        response.update(OrderedDict([
            ('next', paginator.get_next_link()),
            ('previous', paginator.get_previous_link()),
            ('results', data)
        ]))
        conversation.mark_as_read(request.user)
        return Response(response)

    @action(detail=True, methods=['post'], url_path='reply')
    def reply(self, request, **kwargs):
        conversation = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save(
            conversation=conversation,
            user_from=request.user,
        )
        response_serializer = msg_serializers.MessageSerializer(
            message,
            context=self.get_serializer_context(),
        )
        return Response(response_serializer.data)

    @action(detail=False, methods=['post'], url_path='create-group', url_name='create-group')
    def create_group(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversations = serializer.save(
            related_to=self.related_uuid,
            user_from=request.user,
        )
        serializer_class = self.serializers.get('default')
        kwargs = {'many': True}
        kwargs['context'] = self.get_serializer_context()
        serializer = serializer_class(conversations, **kwargs)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='total-unread')
    def total_unread(self, request, **kwargs):
        conversations = self.get_queryset()
        total_unread = sum([conv.total_unread(request.user) for conv in conversations])
        return Response(total_unread)

    @action(detail=False, methods=['get'], url_path='total')
    def total(self, request, **kwargs):
        conversations = self.get_queryset()
        data = {
            'total': 0,
            'unread': 0,
        }
        data['unread'] = sum([conv.total_unread(request.user) for conv in conversations])
        data['total'] = sum([conv.messages.count() for conv in conversations])
        return Response(data)

    @action(detail=True, methods=['put'], url_path='mark-as-read', url_name='mark-as-read')
    def mark_as_read(self, request, **kwargs):
        conversation = self.get_object()
        conversation.mark_as_read(request.user)
        return Response('ok')

    @action(detail=False, methods=['post'], url_path='create-message')
    def create_message(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation_created_by = serializer.validated_data.get('conversation_created_by')
        conversation = Conversation.objects.filter(
            uuid_related_object=self.related_uuid,
            created_by__uuid=conversation_created_by).first()
        if not conversation:
            raise exceptions.NotFound
        serializer.save(
            conversation=conversation)
        return Response()

    @action(detail=False, methods=['put'], url_name='update', url_path='update/(?P<conversation_uuid>[-\\w]+)')
    def update_conversation(self, request, **kwargs):
        conversation = self.get_queryset().get(
            uuid=kwargs.get('conversation_uuid'))
        serializer = self.get_serializer(conversation, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()


class TotalMesagesView(views.APIView):
    permission_classes = (IsAuthenticated,)
    model = Conversation

    def calculate(self, conversations, user):
        data = {
            'total': 0,
            'unread': 0,
        }
        data['unread'] = sum([conv.total_unread(user) for conv in conversations])
        data['total'] = sum([conv.messages.count() for conv in conversations])
        return data

    def post(self, request, *args, **kwargs):
        user = request.user
        related_uuids = request.data.getlist('uuids')
        data = []
        for related_uuid in related_uuids:
            conversations = self.model.objects.filter(
                uuid_related_object=related_uuid,
                users__user=user)
            data.append({
                'uuid': related_uuid,
                'num_messages': self.calculate(conversations, user)})
        return Response(data)
