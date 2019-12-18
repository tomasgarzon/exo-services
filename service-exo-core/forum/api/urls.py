from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from .views import (
    post, post_slug, post_circle,
    questions_team, questions_ecosystem,
    feed, answer)

app_name = 'forum'

router = DefaultRouter()
router.register(
    r'post',
    post.PostViewSet,
    basename='post',
)
router.register(
    r'answer',
    answer.AnswerViewSet,
    basename='answer',
)
router.register(
    r'circles/(?P<circle_slug>[-\w]+)/posts',
    post_circle.PostCircleViewSet,
    basename='circle-post'
)
router.register(
    r'project/(?P<project_pk>\d+)/team/(?P<team_pk>\d+)/questions',
    questions_team.QuestionsTeamViewSet,
    basename='questions-team',
)
router.register(
    r'participant-questions',
    questions_ecosystem.QuestionsEcosystemViewSet,
    basename='questions-participants'
)
router.register(
    r'post-slug',
    post_slug.PostSlugViewSet,
    basename='post-slug'
)

urlpatterns = [
    url(
        r'^',
        include(router.urls),
    ),
    url(
        r'feed/$',
        feed.PostFeedListView.as_view(),
        name='feed',
    ),
]
