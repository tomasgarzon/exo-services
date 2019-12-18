from django.urls import path, include

from .views import (
    generic_feedback_typeform,
    microlearning_typeform
)

app_name = 'typeform'

urlpatterns = [
    path(
        'feedback/',
        generic_feedback_typeform.GenericFeedbackTypeformView.as_view(),
        name='generic-typeform-feedback',
    ),
    path(
        'microlearning/',
        microlearning_typeform.MicroLearningTypeformView.as_view(),
        name='microlearning-typeform',
    ),
    path('', include('typeform_feedback.urls_webhooks')),
]
