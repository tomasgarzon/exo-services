from django.urls import path

from .views import feedback, microlearning


app_name = 'typeform'


urlpatterns = [
    path(
        'feedback/',
        feedback.GenericFeedbackTypeformView.as_view(),
        name='generic-typeform-feedback',
    ),
    path(
        'microlearning/',
        microlearning.MicroLearningTypeformView.as_view(),
        name='microlearning-typeform',
    ),
]
