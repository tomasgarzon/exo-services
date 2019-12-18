from django.conf.urls import url

from .views import message, feedback

urlpatterns = [
    url(r'^messages/$', message.MessagesAPIView.as_view(), name='messages'),
    url(r'^feedback/$', feedback.FeedbackAPIView.as_view(), name='feedback'),
]
