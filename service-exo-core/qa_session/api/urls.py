from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from .views import (
    qa_session_team,
    qa_session_ecosystem,
    question_ecosystem,
    question_team,
    answer,
)

app_name = 'swarms'

router = DefaultRouter()
router.register(
    'ecosystem',
    qa_session_ecosystem.QASessionEcosystemViewSet,
    basename='swarms-ecosystem')
router.register(
    r'ecosystem/(?P<swarm_id>\d+)/questions',
    question_ecosystem.QASessionQuestionEcosystemViewSet,
    basename='swarms-ecosystem-questions'
)
router.register(
    r'ecosystem/(?P<swarm_id>\d+)/questions/(?P<question_id>\d+)/answers',
    answer.QASessionAnswerViewSet,
    basename='swarms-ecosystem-answers'
)
router.register(
    r'project/(?P<project_id>\d+)/team/(?P<team_id>\d+)/swarms',
    qa_session_team.QASessionTeamViewSet,
    basename='swarms-project')

router.register(
    r'project/(?P<project_id>\d+)/team/(?P<team_id>\d+)/swarms/(?P<swarm_id>\d+)/questions',
    question_team.QASessionQuestionTeamViewSet,
    basename='swarms-project-questions')

router.register(
    r'project/(?P<project_id>\d+)/team/(?P<team_id>\d+)/swarms'
    r'/(?P<swarm_id>\d+)/questions/(?P<question_id>\d+)/answers',
    answer.QASessionAnswerViewSet,
    basename='swarms-project-answers')

urlpatterns = [
    url('', include(router.urls)),
]
