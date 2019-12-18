from django.urls import path, include

from rest_framework import routers

from .views import conversation, message


app_name = 'api'

router = routers.SimpleRouter()

router.register(
    r'conversations',
    conversation.ConversationViewSet,
    basename='conversations',
)
router.register(
    r'messages',
    message.MessageViewSet,
    basename='messages',
)

urlpatterns = [
    path('/<uuid:related_uuid>/', include(router.urls)),
    path('/', include(router.urls)),
    path('/total/', conversation.TotalMesagesView.as_view()),
]
