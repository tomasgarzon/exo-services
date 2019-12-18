from rest_framework import routers
from django.urls import path

from .views import survey, question, fill_survey, survey_filled

app_name = 'api'

router = routers.SimpleRouter()

router.register(r'survey', survey.SurveyViewSet, basename='survey')
router.register(r'survey-filled', survey_filled.SurveyFilledViewSet, basename='survey-filled')


urlpatterns = router.urls
urlpatterns += [
    path('questions/', question.QuestionListView.as_view(), name='question-list'),
    path('fill/<slug:slug>/', fill_survey.FillSurveyAPIView.as_view(), name='survey-fill'),
    path('survey-filled/<int:pk>/pdf/', survey_filled.SurveyFilledPDF.as_view(), name='filled-download-pdf'),
    path('check-slug/', survey.CheckSlugAPIView.as_view(), name='check-slug'),
]
